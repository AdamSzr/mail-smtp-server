import base64
from asyncio.streams import StreamReader, StreamWriter
import re

commands = [
    'APPEND', 'AUTHENTICATE', 'CAPABILITY', 'CHECK', 'CLOSE', 'COPY', 'CREATE',
    'DELETE', 'DELETEACL', 'ENABLE', 'EXAMINE', 'EXPUNGE', 'FETCH', 'GETACL',
    'GETANNOTATION', 'GETQUOTA', 'GETQUOTAROOT', 'MYRIGHTS', 'LIST', 'LOGIN',
    'LOGOUT', 'LSUB', 'MOVE', 'NAMESPACE', 'NOOP', 'PARTIAL', 'PROXYAUTH',
    'RENAME', 'SEARCH', 'SELECT', 'SETACL', 'SETANNOTATION', 'SETQUOTA', 'SORT',
    'STARTTLS', 'STATUS', 'STORE', 'SUBSCRIBE', 'THREAD', 'UID', 'UNSUBSCRIBE', 'UNSELECT',
]


class IMAPRequest:
    def __init__(self, request):
        self.request = request
        self.request_str = self.request.decode()

        try:
            parts = list(map(lambda e: e.strip(), self.request_str.split(' ')))
            self.tag = parts[0]
            self.command = parts[1].upper()
            self.rest = parts[2:]
        except:
            print("IMAPRequest - Parse exception occured -->", self.request)


CRLF = '\r\n'
CONTINUATION = f'+{CRLF}'


class IMAPServer:

    def __init__(self, logger):
        self.logger = logger
        self.async_handlers = ['AUTHENTICATE', 'LOGIN']

    def write_to_client(self, req: IMAPRequest, client_writer: StreamWriter, message: str):
        if not message.endswith(CRLF):
            return print('INVALID MESSAGE - not ends with CRLF')
        if message.startswith(' '):
            return print('WRONG MESSAGE - cannot starts with  white-space')

        encoded_mess = message.encode()
        self.logger.log(encoded_mess)
        client_writer.write(encoded_mess)

    def get_bad_response(self, reason: str):
        return f'* BAD Command {reason}.{CRLF}'

    def pick_handler(self, req: IMAPRequest):
        handlers = {
            'CAPABILITY': self.handle_capability_request,
            'LOGOUT': self.handle_logout_request,
            'NOOP': self.handle_noop_request,
            'NAMESPACE': self.handle_namespace_request,
            'ID': self.handle_id_request,
            'UID': self.handle_uid_request,
            'LSUB': self.handle_lsub_request,
            'LIST': self.handle_list_request,
            'XLIST': self.handle_xlist_request,
            'IDLE': self.handle_idle_request,
            'STATUS': self.handle_status_request,
            'SELECT': self.handle_select_request
        }
        return handlers.get(req.command)

    def is_async_handler(self, req: IMAPRequest):
        return req.command in self.async_handlers

    def handle_welcome_message(self, req: IMAPRequest, client_reader: StreamReader, client_writer: StreamWriter):
        welcome_message_resp = f'* OK IMAP4rev1 Server Ready{CRLF}'
        self.write_to_client(req, client_writer, welcome_message_resp)

    def handle_idle_request(self, req: IMAPRequest, client_reader: StreamReader, client_writer: StreamWriter):
        idle_resp = '+ idling'
        self.write_to_client(req, client_writer, idle_resp)

    def handle_status_request(self, req: IMAPRequest, client_reader: StreamReader, client_writer: StreamWriter):
        target_status_dir = req.rest[0]
        remove_quotes = '|' not in target_status_dir
        if remove_quotes:
            target_status_dir = target_status_dir.replace('"', '')
        status_resp = (
                f'* STATUS {target_status_dir} (MESSAGES 0 RECENT 0 UNSEEN 0 UIDNEXT 8){CRLF}' +
                f'{req.tag} OK STATUS Completed.{CRLF}'
        )
        self.write_to_client(req, client_writer, status_resp)

    def handle_capability_request(self, req: IMAPRequest, client_reader: StreamReader, client_writer: StreamWriter):
        capabilities_resp = (
                f'* CAPABILITY IMAP4rev1 CHILDREN UNSELECT LITERAL+ NAMESPACE XLIST UIDPLUS ENABLE ID AUTH=PLAIN MOVE{CRLF}' +
                f'{req.tag} OK CAPABILITY Completed.{CRLF}'
        )
        self.write_to_client(req, client_writer, capabilities_resp)

    def handle_namespace_request(self, req: IMAPRequest, client_reader: StreamReader, client_writer: StreamWriter):
        namespace_resp = (
                f'* NAMESPACE (("" "|")) NIL NIL{CRLF}' +
                f'{req.tag} OK NAMESPACE command completed.{CRLF}'
        )
        self.write_to_client(req, client_writer, namespace_resp)

    def handle_id_request(self, req: IMAPRequest, client_reader: StreamReader, client_writer: StreamWriter):
        id_resp = (
                f'* ID ("name" "Yandex Mail" "vendor" "Yandex" "support-url" "http://feedback.yandex.ru/?from=mail"){CRLF}' +
                f'{req.tag} OK ID command completed.{CRLF}'
        )
        self.write_to_client(req, client_writer, id_resp)

    def handle_noop_request(self, req: IMAPRequest, client_reader: StreamReader, client_writer: StreamWriter):
        response = f'{req.tag} OK NOOP completed.{CRLF}'
        self.write_to_client(req, client_writer, response)

    async def handle_auth_request(self, req: IMAPRequest, client_reader: StreamReader, client_writer: StreamWriter):
        auth_method = req.rest[0].upper()
        if auth_method != 'PLAIN':
            return self.write_to_client(req, client_writer, self.get_bad_response(self, 'auth method not supported'))

        self.write_to_client(req, client_writer, CONTINUATION)

        credentials_encoded = await client_reader.readuntil(CRLF.encode())
        credentials = credentials_encoded
        self.logger.log(credentials)

        response = f'{req.tag} OK PLAIN authenticate Completed.{CRLF}'
        self.write_to_client(req, client_writer, response)

    def handle_login_request(self, req: IMAPRequest, client_reader: StreamReader, client_writer: StreamWriter):
        [login, password] = req.rest
        login_resp = (
                f'* CAPABILITY IMAP4rev1 CHILDREN UNSELECT LITERAL+ NAMESPACE XLIST UIDPLUS ENABLE ID MOVE{CRLF}' +
                f'{req.tag} OK login Completed.{CRLF}'
        )
        self.write_to_client(req, client_writer, login_resp)

    def handle_list_request(self, req: IMAPRequest, client_reader: StreamReader, client_writer: StreamWriter):
        list_resp = (
                f'* list (\HasNoChildren \\Unmarked \\NoInferiors) "|" INBOX {CRLF}' +
                f'{req.tag} OK list Completed. {CRLF}'
        )
        self.write_to_client(req, client_writer, list_resp)

    def handle_lsub_request(self, req: IMAPRequest, client_reader: StreamReader, client_writer: StreamWriter):
        lsub_resp = (
                f'* lsub (\HasChildren \\Unmarked \Drafts) "|" Drafts{CRLF}' +
                f'* lsub (\HasNoChildren \\Unmarked \Templates) "|" "Drafts|template"{CRLF}' +
                f'* lsub (\HasNoChildren \\Unmarked \\NoInferiors) "|" INBOX{CRLF}' +
                f'* lsub (\HasNoChildren \\Unmarked \Sent) "|" Sent{CRLF}' +
                f'* lsub (\HasNoChildren \\Unmarked \Junk) "|" Spam{CRLF}' +
                f'* lsub (\HasNoChildren \Marked \Trash) "|" Trash{CRLF}' +
                f'{req.tag} OK lsub Completed.{CRLF}'
        )
        self.write_to_client(req, client_writer, lsub_resp)

    def handle_xlist_request(self, req: IMAPRequest, client_reader: StreamReader, client_writer: StreamWriter):
        [reference, mailbox_name] = req.rest
        mailbox_name = mailbox_name.replace('"', '')
        xlist_resp = self.get_bad_response('arguments invalid')
        if mailbox_name == '%':
            xlist_resp = (
                    f'* xlist (\HasChildren \\Unmarked \Drafts \Drafts) "|" Drafts {CRLF}' +
                    f'* xlist (\HasNoChildren \\Unmarked \\NoInferiors \Inbox) "|" INBOX {CRLF}' +
                    f'* xlist (\HasNoChildren \\Unmarked) "|" Outbox {CRLF}' +
                    f'* xlist (\HasNoChildren \\Unmarked \Sent \Sent) "|" Sent {CRLF}' +
                    f'* xlist (\HasNoChildren \\Unmarked \Junk \Spam) "|" Spam {CRLF}' +
                    f'* xlist (\HasNoChildren \Marked \Trash \Trash) "|" Trash {CRLF}' +
                    f'{req.tag} OK xlist Completed. {CRLF}'
            )

        if mailbox_name == '%|%':
            xlist_resp = (
                    f'* xlist (\HasNoChildren \\Unmarked \Templates) "|" "Drafts|template"{CRLF}' +
                    f'{req.tag} OK xlist Completed.{CRLF}'
            )

        self.write_to_client(req, client_writer, xlist_resp)

    def handle_logout_request(self, req: IMAPRequest, client_reader: StreamReader, client_writer: StreamWriter):
        message = (
                f'* BYE IMAP4rev1 Server logging out {CRLF}' +
                f'{req.tag} OK LOGOUT completed{CRLF}'
        )
        self.write_to_client(req, client_writer, message)

    def handle_select_request(self, req: IMAPRequest, client_reader: StreamReader, client_writer: StreamWriter):
        select_response = (
                f'* FLAGS (\Answered \Seen \Draft \Deleted $Forwarded) {CRLF}' +
                f'* 1 EXISTS {CRLF}' +
                f'* 0 RECENT {CRLF}' +
                f'* OK [PERMANENTFLAGS (\Answered \Seen \Draft \Flagged \Deleted $Forwarded \*)] Limited {CRLF}' +
                f'* OK [UIDNEXT 28] Ok {CRLF}' +
                f'* OK [UIDVALIDITY 1704221294] Ok {CRLF}' +
                f'{req.tag} OK [READ-WRITE] select Completed. {CRLF}'
        )
        self.write_to_client(req, client_writer, select_response)

    def handle_uid_request(self, req: IMAPRequest, client_reade: StreamReader, client_writer: StreamWriter):
        pattern = r"\(([^()]*(?:\(.*\))?[^()]*)\)"
        try:
            command_name = req.rest[0].upper()
            identifiers = req.rest[1]
        except ValueError:
            command_name = ''
            identifiers = ""
        uid_resp = self.get_bad_response('arguments invalid')

        is_identifires_range = ':' in identifiers and len(identifiers.split(':')) == 2

        match = re.search(pattern, req.request_str)
        message_arg = ''
        message_parts = []
        if match:
            match = match.groups()
            message_arg = match[0]
            message_parts = message_arg.split()


        if len(message_parts) == 1 and message_parts[0] == 'FLAGS':
            uid_resp = f'* 1 FETCH (UID 27 FLAGS (\Seen \Draft)) {CRLF}'

        if command_name == 'MOVE':
            mail_id = int(identifiers)
            uid_resp = (
                    f'* OK[COPYUID 1704221294 {mail_id} {mail_id + 2}]{CRLF}' +
                    f'* 1 EXPUNGE{CRLF}'
            )

        if 'HEADER.FIELDS' in message_arg:
            uid_resp = (
                    f'* 1 FETCH (UID 27 RFC822.SIZE 2190 FLAGS (\Seen \Draft) BODY[HEADER.FIELDS (Reply-To Content-Type In-Reply-To References Newsgroups X-Priority Priority Message-ID Subject Bcc Date Cc To From)] {{245}} {CRLF}' +
                    f'From: rzeka24 rzeka24 <rzeka24@yandex.com>{CRLF}' +
                    f'To: rzeka24 rzeka24 <rzeka24@yandex.com>{CRLF}' +
                    f'Subject: kochanowski zyciorys {CRLF}' +
                    f'Date: Tue, 02 Jan 2024 19:54:31 +0100{CRLF}' +
                    f'Message-Id: <39021704221521@mail.yandex.com>{CRLF}' +
                    f'Content-Type: text/html; charset=utf-8{CRLF}' +
                    f'{CRLF}' +
                    f'){CRLF}'
            )

        if 'BODY.PEEK[]' in message_arg:
            uid_resp = (
                    f'* 1 FETCH (UID 27 RFC822.SIZE 2190 BODY[] {{2190}} {CRLF}' +
                    f'Received: from prvcgftslwhsg7ig.myt.yp-c.yandex.net (prvcgftslwhsg7ig.myt.yp-c.yandex.net [2a02:6b8:c12:3b26:0:640:9da1:0]){CRLF}' +
                    f'    by mail-nwsmtp-mxback-production-main-21.myt.yp-c.yandex.net (mxback/Yandex) with HTTP id TsfOacCO5mI0-AD1UZrnx{CRLF}' +
                    f'    for <rzeka24@yandex.com>; Tue, 02 Jan 2024 21:54:31 +0300{CRLF}' +
                    f'X-Yandex-Fwd: 1{CRLF}' +
                    f'Received: by prvcgftslwhsg7ig.myt.yp-c.yandex.net with HTTP;{CRLF}' +
                    f'    Tue, 02 Jan 2024 21:54:31 +0300{CRLF}' +
                    f'From: rzeka24 rzeka24 <rzeka24@yandex.com>{CRLF}' +
                    f'To: rzeka24 rzeka24 <rzeka24@yandex.com>{CRLF}' +
                    f'Subject: kochanowski zyciorys {CRLF}' +
                    f'MIME-Version: 1.0{CRLF}' +
                    f'X-Mailer: Yamail [ http://yandex.ru ] 5.0{CRLF}' +
                    f'Date: Tue, 02 Jan 2024 19:54:31 +0100{CRLF}' +
                    f'Message-Id: <39021704221521@mail.yandex.com>{CRLF}' +
                    f'Content-Transfer-Encoding: base64{CRLF}' +
                    f'Content-Type: text/html; charset=utf-8{CRLF}' +
                    f'{CRLF}' +
                    f'PGRpdj48ZGl2PjxzcGFuIHN0eWxlPSJiYWNrZ3JvdW5kLWNvbG9yOiNmZmZmZmY7Y29sb3I6IzIx{CRLF}' +
                    f'MjUyOTtmbG9hdDpub25lO2ZvbnQtZmFtaWx5OidhcmNoaXZvJyAsIHNhbnMtc2VyaWY7Zm9udC1z{CRLF}' +
                    f'aXplOjE2cHg7Zm9udC1zdHlsZTpub3JtYWw7Zm9udC13ZWlnaHQ6NDAwO3RleHQtYWxpZ246bGVm{CRLF}' +
                    f'dDt0ZXh0LWRlY29yYXRpb24tY29sb3I6aW5pdGlhbDt0ZXh0LWRlY29yYXRpb24tc3R5bGU6aW5p{CRLF}' +
                    f'dGlhbDt0ZXh0LWluZGVudDowcHg7dGV4dC10cmFuc2Zvcm06bm9uZTt3aGl0ZS1zcGFjZTpub3Jt{CRLF}' +
                    f'YWw7d29yZC1zcGFjaW5nOjBweCI+SmFuIEtvY2hhbm93c2tpIGhlcmJ1IEtvcndpbiAoQ29ydmlu{CRLF}' +
                    f'dXMpLCDFvHnFgiB3IGxhdGFjaCAxNTMwLTE1ODQuIFVyb2R6acWCIHNpxJkgdyBTeWN5bmllIHcg{CRLF}' +
                    f'emllbWkgcmFkb21za2llaiwgdyB3b2pld8OzZHp0d2llIHNhbmRvbWllcnNraW0sIGRpZWNlempp{CRLF}' +
                    f'IGtyYWtvd3NraWVqLiBKZWdvIG9qY2VtIGJ5xYIgUGlvdHIgS29jaGFub3dza2kgKDE0ODUtMTU0{CRLF}' +
                    f'NyksIHPEmWR6aWEgc2FuZG9taWVyc2tpLCBtYXRrxIUgYnnFgmEgQW5uYSB6IEJpYcWCYWN6b3dh{CRLF}' +
                    f'IGhlcmJ1IE9kcm93xIXFvCB6bWFyxYJhIHcgMTU1NyByb2t1LiBKYW4gS29jaGFub3dza2kgYnnF{CRLF}' +
                    f'giBkcnVnaW0geiBrb2xlaSBzeW5lbSwgc3BvxZtyw7NkIGR3YW5hxZtjaW9yZ2EgZHppZWNpLiBK{CRLF}' +
                    f'YW4gamFrbyBkemllY2tvIGJhcmR6byB3aWVsZSB6YXdkemnEmWN6YcWCIG1hdGNlLCBrdMOzcmEg{CRLF}' +
                    f'dWNob2R6acWCYSB6YSBvc29ixJkgbyB3eXJhemlzdGVqIG9zb2Jvd2/Fm2NpLCB1d2llY3puaW9u{CRLF}' +
                    f'YSB6b3N0YcWCYSB3c3DDs8WCY3plxZtuaWUgdyDFm3dpYWRlY3R3YWNoIGxpdGVyYWNraWNoLCB6{CRLF}' +
                    f'd8WCYXN6Y3phIHcgRHdvcnphbmluaWUgxYF1a2FzemEgR8Ozcm5pY2tpZWdvLiBXcMWCeW7EmcWC{CRLF}' +
                    f'YSBuaWV3xIV0cGxpd2llIG5hIHJvenfDs2ogZHVjaG93eSBzd29pY2ggZHppZWNpLCB6IGt0w7Ny{CRLF}' +
                    f'eWNoIGHFvCB0cnplY2ggd2VzesWCbyBkbyBsaXRlcmF0dXJ5LCBKYW4sIE1pa2/FgmFqIGkgQW5k{CRLF}' +
                    f'cnplai48L3NwYW4+PC9kaXY+PC9kaXY+){CRLF}'
            )

        uid_resp += f'{req.tag} OK UID {command_name} Completed. {CRLF}'
        self.write_to_client(req, client_writer, uid_resp)

    async def handle_client(self, client_reader: StreamReader, client_writer: StreamWriter):
        addr = client_writer.get_extra_info('peername')
        self.logger.log(f"New Client --> {addr}")

        self.handle_welcome_message(None, client_reader, client_writer)

        while not client_reader.at_eof():
            thunderbird_req = await client_reader.read(4096)
            if not thunderbird_req:
                break

            client_request = IMAPRequest(thunderbird_req)
            self.logger.log(client_request.request)

            handler = self.pick_handler(client_request)

            if not self.is_async_handler(client_request) and handler is not None:
                handler(client_request, client_reader, client_writer)

            if client_request.command == 'AUTHENTICATE':
                await self.handle_auth_request(client_request, client_reader, client_writer)

            if client_request.command == 'LOGIN':
                self.handle_login_request(client_request, client_reader, client_writer)

            if not self.is_async_handler(client_request) and handler is None:
                self.logger.log('No handler found for client request')
                self.write_to_client(client_request, client_writer,
                                     self.get_bad_response(f'{client_request.command} currently is not supported.'))

            await client_writer.drain()

            if client_request.request == 'LOGOUT':
                break

        print(f"Closing connection with {addr}")
        self.logger.dump()
        client_writer.close()
        await client_writer.wait_closed()
