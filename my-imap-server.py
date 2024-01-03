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

def getFullYandex():
    '''
    OK [(b'2344 (RFC822 {5506}', b'Received: from postback13b.mail.yandex.net (postback13b.mail.yandex.net [2a02:6b8:c02:900:1:45:d181:da13])\r\n\tby dio7yov3iycb7dql.iva.yp-c.yandex.net (notsolitesrv/Yandex) with LMTP id 5y6EHzBXJWfK-S3v96ByT\r\n\tfor <rzeka24@yandex.com>; Tue, 02 Jan 2024 21:56:27 +0300\r\nReceived: from mail-nwsmtp-mxfront-production-main-43.sas.yp-c.yandex.net (mail-nwsmtp-mxfront-production-main-43.sas.yp-c.yandex.net [IPv6:2a02:6b8:c08:1014:0:640:ffc1:0])\r\n\tby postback13b.mail.yandex.net (Yandex) with ESMTPS id 6C1C15E4AC\r\n\tfor <rzeka24@yandex.com>; Tue,  2 Jan 2024 21:56:27 +0300 (MSK)\r\nReceived: from mail-pg1-x52e.google.com (mail-pg1-x52e.google.com [2607:f8b0:4864:20::52e])\r\n\tby mail-nwsmtp-mxfront-production-main-43.sas.yp-c.yandex.net (mxfront/Yandex) with ESMTPS id PufFUAF2ta60-Lc8Kz82Q;\r\n\tTue, 02 Jan 2024 21:56:26 +0300\r\nX-Yandex-Fwd: 1\r\nAuthentication-Results: mail-nwsmtp-mxfront-production-main-43.sas.yp-c.yandex.net; spf=pass (mail-nwsmtp-mxfront-production-main-43.sas.yp-c.yandex.net: domain of gmail.com designates 2607:f8b0:4864:20::52e as permitted sender, rule=[ip6:2607:f8b0:4000::/36]) smtp.mail=mr.honos@gmail.com; dkim=pass header.i=@gmail.com\r\nX-Yandex-Spam: 4\r\nX-Yandex-Uid-Status: 4 1933751457\r\nReceived: by mail-pg1-x52e.google.com with SMTP id 41be03b00d2f7-53fa455cd94so2475848a12.2\r\n        for <rzeka24@yandex.com>; Tue, 02 Jan 2024 10:56:26 -0800 (PST)\r\nDKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;\r\n        d=gmail.com; s=20230601; t=1704221785; x=1704826585; darn=yandex.com;\r\n        h=to:subject:message-id:date:from:mime-version:from:to:cc:subject\r\n         :date:message-id:reply-to;\r\n        bh=nYrWmnhjM/KnlYummHqs3cfUmWMBZppOsNOv5FU3IAE=;\r\n        b=AJMrI0+BDhUaqQTcPdi1z+86X+o9p7cN4qhaNyrCCtnN1p9fKzFX7K58gcFGh2TOuj\r\n         wNNgKF5RfaV8MaYy8dvd6ppdPygCwJGwH7f3Ecx1i0QhdjCLLa9TqgEEP+KNtJYNXKsr\r\n         t43ZndyMD1uAIZ6wNd73zbdx6Psd1yb/SvfXxM7CUW1Zd2LNhOL/KPV/60Fcy2MXQIJf\r\n         YZ1ZFzLx/lkDsACe6wN4/v8EW0kHtDtjbHbwmEXeOkDL5gbBK6nas8+HE9h5Bb+qtbBJ\r\n         KnXPCOFBLxGO7y68lKnFL/PQQSNPfJke9C9j5E11F+Wifl1zjzxfeN+9FXtymr4wIeIu\r\n         FWdQ==\r\nX-Google-DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed;\r\n        d=1e100.net; s=20230601; t=1704221785; x=1704826585;\r\n        h=to:subject:message-id:date:from:mime-version:x-gm-message-state\r\n         :from:to:cc:subject:date:message-id:reply-to;\r\n        bh=nYrWmnhjM/KnlYummHqs3cfUmWMBZppOsNOv5FU3IAE=;\r\n        b=iWSAcZxLo5iY0De4F9ExoLyie3L64mIIjUzULuuytoDHMQtSWDICjFRrKtWPsfymyC\r\n         yCoiXC+TRkwxUWjYNEZ5mdCJBWPCX8+8cHdHkIF4bceM3wFx/4Mncjmo29N7OcClFgx+\r\n         xdYWJvmjXci7p72igdR9wJ+JCnrjqoCIVhKv2sbC5rVr744c75mMFEKpUPCp6ORtY+SA\r\n         4wR7XR/4AZoy6xPh1VMA1lssct88+51+tal3FCUiCLpvUwBHUKSEi7GBPvwwFz5YNAq6\r\n         vM7EWnYsRUWE6wn4n918v48a98SFUWc5VBPr3WL7fI53bVslWeTAsAKdMJ0ToW17taT1\r\n         MCwQ==\r\nX-Gm-Message-State: AOJu0Yw1fSIqKi4ZRSGvWNN685k2CBjaeJ/u01CtrFzg712tuFxZoCKW\r\n\tqI8l2jKRL9z2T9VaIlsadjHfbA7A7VTSOSm39k04EUPu1+8=\r\nX-Google-Smtp-Source: AGHT+IEzDpToMTJ70n8WkdSFgO0+4CmIePD+rPuye4j2+52GJyKBrAYVaYskKBBXVqw9N3BRjuZDpk1C9kgV/DySrf0=\r\nX-Received: by 2002:a25:5f4e:0:b0:dbc:fb03:6ec with SMTP id\r\n h14-20020a255f4e000000b00dbcfb0306ecmr7462681ybm.125.1704221404414; Tue, 02\r\n Jan 2024 10:50:04 -0800 (PST)\r\nMIME-Version: 1.0\r\nFrom: Adam Szreiber <mr.honos@gmail.com>\r\nDate: Tue, 2 Jan 2024 19:49:53 +0100\r\nMessage-ID: <CAKRCm1cVfay6hRyfnbqoKkCrSr68yDiw3SOdkuMQH5Ap4k80vQ@mail.gmail.com>\r\nSubject: =?UTF-8?Q?test_mail_=2D_kochanowski_na_lip=C4=99?=\r\nTo: rzeka24@yandex.com\r\nContent-Type: multipart/alternative; boundary="0000000000006dc6be060dfaf7d8"\r\nReturn-Path: mr.honos@gmail.com\r\nX-Yandex-Forward: 4cf040059aaec3feb08c9e675ba06734\r\n\r\n--0000000000006dc6be060dfaf7d8\r\nContent-Type: text/plain; charset="UTF-8"\r\nContent-Transfer-Encoding: quoted-printable\r\n\r\nGo=C5=9Bciu, si=C4=85d=C5=BA pod mym li=C5=9Bciem, a odpoczni sobie!\r\nNie dojdzie ci=C4=99 tu s=C5=82o=C5=84ce, przyrzekam ja tobie,\r\nCho=C4=87 si=C4=99 nawysszej wzbije, a proste promienie\r\n=C5=9Aci=C4=85gn=C4=85 pod swoje drzewa rozstrzelane cienie.\r\nTu zaw=C5=BCdy ch=C5=82odne wiatry z pola zawiewaj=C4=85,\r\nTu s=C5=82owicy, tu szpacy wdzi=C4=99cznie narzekaj=C4=85.\r\nZ mego wonnego kwiatu pracowite pszczo=C5=82y\r\nBior=C4=85 mi=C3=B3d, kt=C3=B3ry potym szlachci pa=C5=84skie sto=C5=82y.\r\nA ja swym cichym szeptem sprawi=C4=87 umiem snadnie,\r\n=C5=BBe cz=C5=82owiekowi =C5=82acno s=C5=82odki sen przypadnie.\r\nJab=C5=82ek wprawdzie nie rodz=C4=99, lecz mi=C4=99 pan tak k=C5=82adzie\r\nJako szczep nap=C5=82odniejszy w hesperyskim sadzie.\r\n\r\n--0000000000006dc6be060dfaf7d8\r\nContent-Type: text/html; charset="UTF-8"\r\nContent-Transfer-Encoding: quoted-printable\r\n\r\n<div dir=3D"ltr">Go=C5=9Bciu, si=C4=85d=C5=BA pod mym li=C5=9Bciem, a odpoc=\r\nzni sobie!<br>Nie dojdzie ci=C4=99 tu s=C5=82o=C5=84ce, przyrzekam ja tobie=\r\n,<br>Cho=C4=87 si=C4=99 nawysszej wzbije, a proste promienie<br>=C5=9Aci=C4=\r\n=85gn=C4=85 pod swoje drzewa rozstrzelane cienie.<br>Tu zaw=C5=BCdy ch=C5=\r\n=82odne wiatry z pola zawiewaj=C4=85,<br>Tu s=C5=82owicy, tu szpacy wdzi=C4=\r\n=99cznie narzekaj=C4=85.<br>Z mego wonnego kwiatu pracowite pszczo=C5=82y<b=\r\nr>Bior=C4=85 mi=C3=B3d, kt=C3=B3ry potym szlachci pa=C5=84skie sto=C5=82y.<=\r\nbr>A ja swym cichym szeptem sprawi=C4=87 umiem snadnie,<br>=C5=BBe cz=C5=82=\r\nowiekowi =C5=82acno s=C5=82odki sen przypadnie.<br>Jab=C5=82ek wprawdzie ni=\r\ne rodz=C4=99, lecz mi=C4=99 pan tak k=C5=82adzie<br>Jako szczep nap=C5=82od=\r\nniejszy w hesperyskim sadzie.<br></div>\r\n\r\n--0000000000006dc6be060dfaf7d8--\r\n'), b')']
    '''


def getMail():
    return (
        f'* 1 FETCH (UID 2344 RFC822.SIZE 3456 FLAGS (\Seen) BODY.PEEK[HEADER.FIELDS (From To Cc Bcc Subject Date Message-ID Priority X-Priority References Newsgroups In-Reply-To Content-Type Reply-To)] 342\r\n'
        f'MIME-Version: 1.0\r\n'
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

            decoded_data = data.decode()
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
                    writer.write(response.encode())
                    await writer.drain()
                    credentials_encoded = await reader.read(4096)
                    credentials = credentials_encoded
                    print('credentials -> ', decode_credentials(credentials))
                    response = f'{tag} OK AUTHENTICATE completed\r\n'
            elif 'SELECT' in command.upper():
                response = (
                                f'* FLAGS (\Answered \Flagged \Deleted \Seen \Draft)\r\n'
                                f'* OK [PERMANENTFLAGS (\Answered \Flagged \Deleted \Seen \Draft \*)] Flags permitted.\r\n'
                                f'* 1 EXISTS\r\n'
                                f'* 0 RECENT\r\n'
                                f'* OK [UIDVALIDITY 1234] UIDs valid.\r\n'
                                f'* OK [UIDNEXT 2345] Predicted next UID.\r\n'
                                f'{tag} OK [READ-WRITE] SELECT completed\r\n'
                            )
            elif 'UID' in command.upper():
                if not any('RFC822' in element.upper() for element in rest):
                    response = (
                        f'* 1 FETCH (UID 2344 FLAGS (\Seen))\r\n'
                        f'{tag} OK FETCH completed\r\n'
                    )
                else:
                    response = (
                        f'* 1 FETCH (UID 2344 RFC822.SIZE 5048 FLAGS (\\Seen encrypted) BODY[HEADER.FIELDS (Reply-To Content-Type In-Reply-To References Newsgroups X-Priority Priority Message-ID Subject Bcc Date Cc To From)] {310}\r\n'
                        f'{tag}  OK UID FETCH Completed.\r\n'
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

            writer.write(response.encode())
            await writer.drain()

            print('###')
            print(response.strip())
            print('###\r\n')

        print(f"Closing connection with {addr}")
        writer.close()
        await writer.wait_closed()

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
