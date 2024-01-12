from my_utils import get_acctual_time
from datetime import datetime


class Logger():
    def __init__(self, log_with_date=True):
        self.messages = []
        self.log_with_date = log_with_date

    def dump(self, file_name='logs', separator=''):
        try:
            formatted_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            with open(file_name + '_' + formatted_date + '.txt', 'w') as file:
                for string in self.messages:
                    file.write(string + separator)
        except Exception as e:
            print(f"Wystąpił błąd podczas zapisywania do pliku: {str(e)}")

    def __log_prefix(self):
        if self.log_with_date:
            return f'{get_acctual_time()}'

    def log(self, data):
        message = f'|[ {self.__log_prefix()} ]| {data}'
        print(message)
        self.messages.append(message)
