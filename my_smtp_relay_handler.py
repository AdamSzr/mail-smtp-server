import dns.resolver
import smtplib
from aiosmtpd.handlers import AsyncMessage
from email.message import EmailMessage
import asyncio

class RelayHandler(AsyncMessage):
    async def handle_message(self, message: EmailMessage):
        # Otrzymaj adres e-mail odbiorcy
        recipient = message['To']
        domain = recipient.split('@')[-1]

        # Wyszukaj rekordy MX dla domeny
        mx_records = dns.resolver.resolve('adamszr.com', 'MX')
        mx_record = sorted(mx_records, key=lambda record: record.preference)[0]
        mx_host = str(mx_record.exchange).rstrip('.')

        # Przekaż wiadomość do serwera MX
        try:
            await asyncio.to_thread(self.relay_email, mx_host, message)
            print(f"Email przekazany do {mx_host}")
        except Exception as e:
            print(f"Błąd podczas przekazywania e-maila: {e}")

    def relay_email(self, mx_host, message: EmailMessage):
        with smtplib.SMTP(mx_host) as server:
            print(server.send_message(message))


# Przy użyciu RelayHandler w Twoim kontrolerze
# controller = Controller(RelayHandler(), hostname='127.0.0.1', port=8025)
# controller.start()
