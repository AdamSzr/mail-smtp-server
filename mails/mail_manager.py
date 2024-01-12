import os

mails_registry = {
    '33': 'kochanowski-zyciorys.eml',
    '34':  'kochanowski-na-lipe.eml',
    '35': 'test-raw-text-message.eml',
    '36': 'kochanowski-na-zdrowie.eml'
}

def getMail():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    print(current_directory)

def getFetchReponses():
   response = '''* 1 FETCH (UID 33 FLAGS (\Seen \Draft))
      * 2 FETCH (UID 34 FLAGS (\Seen encrypted))
      * 3 FETCH (UID 35 FLAGS (\Seen encrypted))
      * 4 FETCH (UID 36 FLAGS (\Seen \Draft))
   '''