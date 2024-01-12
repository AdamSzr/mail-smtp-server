from datetime import datetime
import base64

def get_acctual_time():
    date_now = datetime.now()
    return date_now.strftime('%H:%M:%S')

def decode_credentials(self, credentials):
    parts = base64.b64decode(credentials).decode('utf-8').split('\x00')
    return [part for part in parts if part != '']
