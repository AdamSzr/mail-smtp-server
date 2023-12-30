import asyncio
import base64

def decode_credentials(credentials):
    parts = base64.b64decode(credentials).decode('utf-8').split('\x00')
    return [part for part in parts if part != '']


def prepare_UID_response():
    wiersz = [
        "Nie porzucaj nadzieje",
        "Nawet w najgorsze dni",
        "W sercu zawsze miej nadzieje",
        "A wszystko się odmieni"
    ]

    prepared_messages = []
    # Symulowanie odpowiedzi serwera IMAP
    for i, wers in enumerate(wiersz, start=1):
        flags = "\\Seen" if i % 2 == 0 else "\\Answered"  # Przykładowe flagi
        prepared_messages.append(f"* {i} FETCH (FLAGS ({flags}) UID {i} BODY[TEXT] {{{len(wers)}}}\r\n{wers}\r\n)")

    return prepared_messages


def get_mails():
    return '''
    * 1 FETCH 1 (UID 1234 RFC822.SIZE 4567 FLAGS (\Seen) BODY[HEADER.FIELDS (From To Cc Bcc Subject Date Message-ID Priority X-Priority References Newsgroups In-Reply-To Content-Type Reply-To)] {123}'
    From: example@example.com
    To: recipient@example.com
    Cc: cc@example.com
    Bcc: bcc@example.com
    Subject: Sample Subject
    Date: Fri, 30 Dec 2023 12:00:00 +0000
    Message-ID: <123456789@example.com>
    Priority: Normal
    X-Priority: 3
    References: <987654321@example.com>
    Newsgroups: example.group
    In-Reply-To: <987654321@example.com>
    Content-Type: text/plain; charset="utf-8"
    Reply-To: reply@example.com)

    * 2 FETCH 2 (UID 5678 RFC822.SIZE 7890 FLAGS (\Seen) BODY[HEADER.FIELDS (From To Cc Bcc Subject Date Message-ID Priority X-Priority References Newsgroups In-Reply-To Content-Type Reply-To)] {456}
    From: another@example.com
    To: recipient@example.com
    Cc: cc@example.com
    Bcc: bcc@example.com
    Subject: Another Subject
    Date: Sat, 31 Dec 2023 12:00:00 +0000
    Message-ID: <987654321@example.com>
    Priority: High
    X-Priority: 1
    References: <123456789@example.com>
    Newsgroups: example.group
    In-Reply-To: <123456789@example.com>
    Content-Type: text/plain; charset="utf-8"
    Reply-To: reply@example.com)
    '''


class IMAPServer:
    def __init__(self):
        self.selected_mailbox = None

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"Connected with {addr}")
        mails = prepare_UID_response()

        # Wysyłanie odpowiedzi powitalnej
        welcome_message = '* OK IMAP4rev1 Server Ready\r\n'
        writer.write(welcome_message.encode())
        await writer.drain()

        # Czytanie danych do momentu zamknięcia przez klienta
        while not reader.at_eof():
            data = await reader.read(4096)
            if not data:
                break

            decoded_data = data.decode()
            tag, command, *rest = decoded_data.split(' ')

            print(f'|[ REQ {tag} ]|')
            print(decoded_data.strip())
            print(f"Recived tag: {tag}", f"Received command: {command} || rest ->", rest)
            response = f'{tag} BAD \r\n'

            if 'NOOP' in command.upper():
                response = f'{tag} OK NOOP Completed\r\n'
            elif 'SEARCH' in command.upper():
                response = f'* SEARCH 2 3 5\r\n{tag} OK SEARCH completed\r\n'
            elif 'LOGIN' in command.upper():
                response = f'{tag} OK LOGIN Completed\r\n'
            elif 'AUTHENTICATE' in command.upper():
                auth_method = rest[0].strip().upper()
                if auth_method == 'PLAIN':
                    response = '+\r\n'
                    writer.write(response.encode())
                    await writer.drain()
                    credentials_encoded = await reader.read(4096)
                    credentials = credentials_encoded
                    print('credentials -> ', decode_credentials(credentials))
                    response = f'{tag} OK AUTHENTICATE completed\r\n'
            elif 'SELECT' in command.upper():
                response = (
                                f'* 2 EXISTS\r\n'
                                f'* 0 RECENT\r\n'
                                f'* OK [UNSEEN 1] Message 1 is first unseen\r\n'
                                f'* OK [UIDVALIDITY 123456] UIDVALIDITY value\r\n'
                                f'* OK [UIDNEXT 3] The next unique identifier value\r\n'
                                f'{tag} OK [READ-WRITE] SELECT completed\r\n'
                            )
            elif 'UID' in command.upper():
                if not any('RFC822' in element.upper() for element in rest):
                    response = (
                        f'* 1 FETCH (FLAGS (\Seen) UID 1)\r\n'
                        f'* 2 FETCH (FLAGS (\Seen) UID 2)\r\n'
                        f'{tag} OK FETCH completed\r\n'
                    )
                else:
                    response = f'{get_mails()}{tag} OK FETCH completed\r\n'
                # for index, mail in enumerate(mails):
                #     writer.write(mail.encode())
                #     await writer.drain()
                #     print('send mail idx ->', index)
                # response = f'{tag} OK UID completed\r\n'
            elif 'CAPABILITY' in command.upper():
                response = f'* CAPABILITY IMAP4rev1  AUTH=PLAIN\r\n{tag} OK CAPABILITY Completed\r\n'
            elif 'CHECK' in command.upper():
                response = f'{tag} OK CHECK Completed\r\n'
            elif 'LIST' in command.upper():
                response = f'* LIST (\\Noselect) "/" "" \r\n{tag} OK LIST completed\r\n'
            elif 'LOGOUT' in command.upper():
                response = f'* BYE IMAP4rev1 Server logging out \r\n{tag} OK LOGOUT completed\r\n'

            # Sprawdzenie, czy odpowiedź kończy się na "\r\n"
            if not response.endswith("\r\n"):
                print("Odpowiedź nie kończy się na '\\r\\n'")

            writer.write(response.encode())
            await writer.drain()

            print('###')
            print(response.strip())
            print('###\r\n')

        print(f"Closing connection with {addr}")
        writer.close()
        await writer.wait_closed()

async def main():
    server = IMAPServer()
    imap_server = await asyncio.start_server(
        server.handle_client, 'localhost', 143)

    addr = imap_server.sockets[0].getsockname()
    print(f'Serving IMAP on {addr}')

    async with imap_server:
        await imap_server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
