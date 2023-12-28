import asyncio

class IMAPServer:
    def __init__(self):
        self.selected_mailbox = None

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info('peername')
        print(f"Connected with {addr}")

        # Wysyłanie odpowiedzi powitalnej
        welcome_message = '* OK IMAP4rev1 Server Ready\r\n'
        writer.write(welcome_message.encode())
        await writer.drain()

        # Czytanie danych do momentu zamknięcia przez klienta
        while not reader.at_eof():
            data = await reader.read(4096)
            if not data:
                break

            tag, command = data.decode().split(' ')
            print(f"Received command: {command}")

            if 'SELECT' in command.upper():
                self.selected_mailbox = command.split()[1]
                response = f'* FLAGS (\\Seen \\Deleted)\r\n* OK [PERMANENTFLAGS (\\Seen \\Deleted \\*)] Flags permitted.\r\n* 0 EXISTS\r\n* 0 RECENT\r\nOK [READ-WRITE] SELECT completed\r\n'
            elif 'CAPABILITY' in command.upper():
                response = f'* CAPABILITY IMAP4rev1  LOGINDISABLED\r\n{tag} OK CAPABILITY Completed\r\n'
            elif 'CHECK' in command.upper():
                response = f'{tag} OK CHECK Completed\r\n'
            elif 'NOOP' in command.upper():
                response = f'{tag} OK NOOP Completed\r\n'
            elif 'LOGOUT' in command.upper():
                response = f'* BYE IMAP4rev1 Server logging out \r\n{tag} OK LOGOUT completed'

            writer.write(response.encode())
            await writer.drain()
            print('stopped connection')

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
