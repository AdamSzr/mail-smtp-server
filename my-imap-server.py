import asyncio
import base64
import imap_handlers.proxy_client

use_proxy = True
yandex_client = imap_handlers.proxy_client.getPreparedClient()

def decode_credentials(credentials):
    parts = base64.b64decode(credentials).decode('utf-8').split('\x00')
    return [part for part in parts if part != '']


def getMail():
    return (
        f'* 1 FETCH (UID 2344 RFC822.SIZE 5048 FLAGS (\Seen encrypted) BODY.PEEK[HEADER.FIELDS (From To Cc Bcc Subject Date Message-ID Priority X-Priority References Newsgroups In-Reply-To Content-Type Reply-To)] {{310}}\r\n'
        f'From: nadawca@example.com\r\n'
        f'To: odbiorca@example.com\r\n'
        f'Subject: Przykładowy temat wiadomości\r\n'
        f'Date: Wed, 8 Apr 2024 12:34:56 +0200\r\n'
        f'Message-ID: <1234567890@example.com>\r\n'
        f'Content-Type: text/plain; charset="UTF-8"\r\n'
        f'\r\n'
        f')\r\n'
    )


class IMAPServer:
    def __init__(self):
        self.selected_mailbox = None

    async def handle_client(self, thunderbird_reader, thunderbird_writer): # reader / writer  is a thunderbird socket

        addr = thunderbird_writer.get_extra_info('peername')
        print(f"Connected with {addr}")

        # Wysyłanie odpowiedzi powitalnej
        welcome_message = '* OK IMAP4rev1 Server Ready\r\n'
        thunderbird_writer.write(welcome_message.encode())
        await thunderbird_writer.drain()

        # Czytanie danych do momentu zamknięcia przez klienta
        while not thunderbird_reader.at_eof():
            thunderbird_req = await thunderbird_reader.read(4096)
            if not thunderbird_req:
                break

            decoded_data = thunderbird_req.decode()

            tag, command, *rest = decoded_data.split(' ')

            print(f'|[ REQ {tag} ]|')
            print(decoded_data.strip())
            print(f"Received command: {command.strip()} || rest -> { [part.strip() for part in rest] }")
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
                    thunderbird_writer.write(response.encode())
                    await thunderbird_writer.drain()
                    credentials_encoded = await thunderbird_reader.read(4096)
                    credentials = credentials_encoded
                    print('credentials -> ', decode_credentials(credentials))
                    response = f'{tag} OK AUTHENTICATE completed\r\n'
            elif 'SELECT' in command.upper():
                response = (
                                f'* FLAGS (\Answered \Flagged \Deleted \Seen \Draft)\r\n'
                                f'* OK [PERMANENTFLAGS (\Answered \Flagged \Deleted \Seen \Draft \*)] Flags permitted.\r\n'
                                f'* 1 EXISTS\r\n'
                                f'* 0 RECENT\r\n'
                                f'* OK [UIDVALIDITY 2344] UIDs valid.\r\n'
                                f'* OK [UIDNEXT 2345] Predicted next UID.\r\n'
                                f'{tag} OK [READ-WRITE] SELECT completed\r\n'
                            )
            elif 'UID' in command.upper():
                if not any('RFC822' in element.upper() for element in rest):
                    response = (
                        f'* 1 FETCH (UID 2344 FLAGS (\Seen))\r\n'
                        f'{tag} OK FETCH completed\r\n'
                    )
                elif any('BODY.PEEK[]' in element.upper() for element in rest):
                   response = (
                      f'* 1 FETCH (UID 2344 RFC822.SIZE 229 BODY[] {{229}}\r\n'
                      f'Content-Type: text/plain; charset="UTF-8"\r\n'
                      f'From: nadawca@example.com\r\n'
                      f'To: odbiorca@example.com\r\n'
                      f'Subject: Przykładowy Temat\r\n'
                      f'Date: Thu, 1 Jan 2024 12:00:00 +0000\r\n'
                      f'Message-ID: <1234567890@example.com>\r\n'
                      f'\r\n'
                      f'To jest treść wiadomości.\r\n'
                      f')\r\n'
                      f'{tag} OK UID FETCH Completed.\r\n'
                   )
                else:
                    response = (
                        f'* 1 FETCH (UID 2344 RFC822.SIZE 229 FLAGS (\\Seen encrypted) BODY[HEADER.FIELDS (Reply-To Content-Type In-Reply-To References Newsgroups X-Priority Priority Message-ID Subject Bcc Date Cc To From)] {{310}})\r\n'
                        f'{tag} OK UID FETCH Completed.\r\n'
                    )
            elif 'CAPABILITY' in command.upper():
                response = f'* CAPABILITY IMAP4rev1 AUTH=PLAIN\r\n{tag} OK CAPABILITY Completed\r\n'
            elif 'CHECK' in command.upper():
                response = f'{tag} OK CHECK Completed\r\n'
            elif 'LIST' in command.upper():
                response = f'* LIST (\\Noselect) "/" "" \r\n{tag} OK LIST completed\r\n'
            elif 'LOGOUT' in command.upper():
                response = f'* BYE IMAP4rev1 Server logging out \r\n{tag} OK LOGOUT completed\r\n'

            # Sprawdzenie, czy odpowiedź kończy się na "\r\n"
            if not response.endswith("\r\n"):
                print("Odpowiedź nie kończy się na '\\r\\n'")

            thunderbird_writer.write(response.encode())
            await thunderbird_writer.drain()

            print('###')
            print(response.strip())
            print('###\r\n')

        print(f"Closing connection with {addr}")
        thunderbird_writer.close()
        await thunderbird_writer.wait_closed()

async def main():
    # 115.6.0 (64-bit)
    server = IMAPServer()
    imap_server = await asyncio.start_server(
        server.handle_client, 'localhost', 1430)

    addr = imap_server.sockets[0].getsockname()
    print(f'Serving IMAP on {addr}')

    async with imap_server:
        await imap_server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
