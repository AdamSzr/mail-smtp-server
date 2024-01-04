import imaplib
import email

# IMAP
key = 'tnypwvqyyyqhviif' #
host ='imap.yandex.com'
port = 993
login = 'rzeka24' # rzeka24@yandex.com
passw = key # adam123%%

def getPreparedClient():
    client = imaplib.IMAP4_SSL(host, port)
    login_status, message = client.login(login, passw)
    if(login_status!='OK'):
        print('CANT CONNECT TO ')
        return None

    return client

