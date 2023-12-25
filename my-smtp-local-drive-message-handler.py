from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP as Server, syntax, Session
from aiosmtpd.handlers import Sink, AsyncMessage
import datetime
import asyncio
import base64
from email.utils import parsedate_to_datetime
import json
import traceback


class LocalStorageHandler(AsyncMessage):
    def __init__(self, directory='emails'):
        # Utwórz katalog do przechowywania e-maili, jeśli nie istnieje
        os.makedirs(directory, exist_ok=True)
        self.directory = directory

    async def handle_message(self, message: EmailMessage):
        try:
            # Asynchroniczne wywołanie metody zapisu
            await asyncio.to_thread(self.save_message, message)
        except Exception as e:
            print("Błąd podczas zapisywania wiadomości:", e)
            traceback.print_exc()

    def save_message(self, message: EmailMessage):
        # Utwórz unikalny identyfikator dla każdej wiadomości, na przykład na podstawie daty i czasu
        message_id = message.get('Message-ID') or self.generate_message_id(message)
        file_path = os.path.join(self.directory, f'{message_id}.json')

        # Konwersja wiadomości na format JSON
        message_dict = {
            "subject": message.get('Subject', ''),
            "from": message.get('From', ''),
            "to": message.get('To', ''),
            "date": message.get('Date', ''),
            "body": message.get_payload()
        }

        # Zapisz wiadomość w formacie JSON
        with open(file_path, 'w') as file:
            json.dump(message_dict, file, indent=4, ensure_ascii=False)

    def generate_message_id(self, message: EmailMessage):
        # Generuj identyfikator wiadomości na podstawie daty, jeśli Message-ID nie istnieje
        date_tuple = parsedate_to_datetime(message.get('Date'))
        timestamp = date_tuple.timestamp() if date_tuple else time.time()
        return f"msg-{int(timestamp)}"
