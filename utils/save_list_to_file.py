from datetime import datetime


def save_list_to_file(string_list, file_name, separator=''):
    try:
        # Formatujemy datę i godzinę
        formatted_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Otwieramy plik do zapisu w trybie tekstowym
        with open(file_name + '-' + formatted_date, 'w') as file:
            # Zapisujemy każdy element listy do pliku
            for string in string_list:
                file.write(string + separator)

            # Dodajemy sformatowaną datę na końcu pliku
            file.write(f"Data zapisu: {formatted_date}\n")
            file.close()

        print(f"Zapisano listę do pliku {file_name} z datą {formatted_date}.")
    except Exception as e:
        print(f"Wystąpił błąd podczas zapisywania do pliku: {str(e)}")
