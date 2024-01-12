import imaplib
import email
import socket
import asyncio
import base64
from urllib import request
from datetime import datetime

# IMAP
yandex_key = 'cksdoelpafgqccyp'  #
yandex_host = 'imap.yandex.com'
yandex_port = 993
yandex_login = 'rzeka24'  # rzeka24@yandex.com
yandex_passw = yandex_key  # adam123%%


breaking_keywords = [ 'COMPLETED', '+ IDLING' ] #,'OK', 'BAD', 'NO'
# PROXY SERVER
# which imitates real server.
# but its only reads data from IMAP client (f.e thunderbird)
# and sends it to real server (in this case yandex email)

proxy_server_host = "localhost"  # Standard loopback interface address (localhost)
proxy_server_port = 143  # Port to listen on (non-privileged ports are > 1023)

def getPreparedClient():
    client = imaplib.IMAP4_SSL(yandex_host, yandex_port)
    return client

messages = []

prefix_yandex = 'server >'
prefix_imap_client = 'client >'

def save_list_to_file(string_list, file_name, separator=''):
    try:
        formatted_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        with open(file_name + '_' + formatted_date+'.txt', 'w') as file:
            for string in string_list:
                file.write(string + separator)
    except Exception as e:
        print(f"Wystąpił błąd podczas zapisywania do pliku: {str(e)}")

def handle_communication(data, data_from):
    print(f'|[{data_from}]| {data}')

    if isinstance(data, bytes):
        print("Variable 'data' is of type 'bytes'")
    messages.append(f'{data_from} {data}')


def decode_credentials(credentials):
    parts = base64.b64decode(credentials).decode('utf-8').split('\x00')
    return [part for part in parts if part != '']


class IMAPServer:
    def __init__(self):
        self.selected_mailbox = None

    async def handle_client(self, thunderbird_reader, thunderbird_writer): # reader / writer  is a thunderbird socket
        addr = thunderbird_writer.get_extra_info('peername')
        print(f"Connected with {addr}")

        # na początku serwer imap wysyła podstawowe info welcome message.
        # client by default sends and recives welcome message.
        imap_client = getPreparedClient()
        welcome_message = '* OK IMAP4rev1 Server Ready\r\n'
        handle_communication(welcome_message, prefix_yandex)
        handle_communication('DMJG0 CAPABILITY\r\n', prefix_imap_client)
        handle_communication('* CAPABILITY IMAP4rev1 CHILDREN UNSELECT LITERAL+ NAMESPACE XLIST UIDPLUS ENABLE ID AUTH=PLAIN AUTH=XOAUTH2 IDLE MOVE\r\n',prefix_yandex)
        handle_communication('DMJG0 OK CAPABILITY Completed.\r\n',prefix_yandex)

        thunderbird_writer.write(welcome_message.encode())
        await thunderbird_writer.drain()

        while not thunderbird_reader.at_eof():
            # teraz serwer oczekuja na zapytania od klienta.
            thunderbird_req = await thunderbird_reader.read(4096)
            if not thunderbird_req:
                break

            decoded_thunderbird_req = thunderbird_req.decode()

            if 'SAVE' in decoded_thunderbird_req:
                save_list_to_file(messages, 'comm')
                continue


            # save request from thunderbird
            handle_communication(decoded_thunderbird_req, prefix_imap_client),

            if 'authenticate' in decoded_thunderbird_req:
                tag = decoded_thunderbird_req.split(' ')[0]
                response = '+\r\n'
                handle_communication(response, prefix_yandex)
                thunderbird_writer.write(response.encode())
                await thunderbird_writer.drain()
                credentials_encoded = await thunderbird_reader.read(4096)
                credentials = credentials_encoded
                handle_communication(credentials_encoded.decode(), prefix_imap_client)
                print('auth credentials -> ', decode_credentials(credentials))
                response = f'{tag[0]} OK PLAIN authenticate Completed.\r\n'
                handle_communication(response, prefix_yandex)
                thunderbird_writer.write(response.encode())
                await thunderbird_writer.drain()
                continue

            if 'login' in decoded_thunderbird_req:
                # login_status, message = imap_client.login(yandex_login, yandex_passw)
                tag, command, *rest = decoded_thunderbird_req.split(' ')
                my_req = f'{tag} login "{yandex_login}" "{yandex_passw}"\r\n'
                imap_client.send(my_req.encode())
                handle_communication(my_req, prefix_imap_client)
                credentials = list(map(lambda a: a.strip(), rest[2:]))
                print('login credentials -> ', credentials)
                login_resp = []
                while True:
                    login_resp_line = imap_client.readline()
                    login_resp.append(login_resp_line)
                    resp_text = login_resp_line.decode().upper()
                    if any(keyword in resp_text for keyword in breaking_keywords):
                        break

                full_yandex_login_resp = b''.join(login_resp)
                thunderbird_writer.write(full_yandex_login_resp)
                handle_communication(full_yandex_login_resp.decode(),prefix_yandex)
                await thunderbird_writer.drain()
                continue

            # send request to yandex via yandex-client
            imap_client.send(thunderbird_req)
            # handle_communication(thunderbird_req.decode(), prefix_imap_client)

            # revice data from yandex via yandex-client

            if 'IDLE' in decoded_thunderbird_req:
                print('saving to file')
                save_list_to_file(messages,'comm')

            yandex_server_data = []
            while True:
                line = imap_client.readline()
                yandex_server_data.append(line)
                line_str = line.decode().upper()
                print(f'--> {line_str} <--')
                if any(keyword.upper() in line_str for keyword in breaking_keywords):
                    break


            yandex_resp = b''.join(yandex_server_data)

            # save response from yandex
            handle_communication(''.join(list(map(lambda a: a.decode(), yandex_server_data))), prefix_yandex),

            # send data to thunderbid
            thunderbird_writer.write(yandex_resp)



        print(f"Closing connection with {addr}")
        thunderbird_writer.close()
        await thunderbird_writer.wait_closed()



async def run_server():
    imap_server = IMAPServer()

    server = await asyncio.start_server(imap_server.handle_client, proxy_server_host, proxy_server_port)
    print(f'IMAP server runs ->  |[ {proxy_server_host}:{proxy_server_port} ]|')
    async with server:
        await server.serve_forever()

asyncio.run(run_server())


