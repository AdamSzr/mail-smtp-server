import socket
import ssl
import threading

# Parametry Yandex IMAP
yandex_host = 'imap.yandex.com'
yandex_port = 993
yandex_login = 'rzeka24'
yandex_key = 'tnypwvqyyyqhviif'

# Parametry serwera proxy
proxy_server_host = "localhost"
proxy_server_port = 143

def client_handler(client_socket):
    # Połączenie z serwerem Yandex
    context = ssl.create_default_context()
    yandex_socket = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=yandex_host)
    yandex_socket.connect((yandex_host, yandex_port))

    while True:
        # Odbieranie danych od klienta i wysyłanie do Yandex
        client_data = client_socket.recv(4096)
        if not client_data:
            break
        yandex_socket.sendall(client_data)


        # Odbieranie danych od Yandex i wysyłanie do klienta
        yandex_data = yandex_socket.recv(4096)
        if not yandex_data:
            break
        client_socket.sendall(yandex_data)

    client_socket.close()
    yandex_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((proxy_server_host, proxy_server_port))
    server_socket.listen(5)
    print("Serwer proxy IMAP działa i nasłuchuje...")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            client_thread = threading.Thread(target=client_handler, args=(client_socket,))
            client_thread.start()
    except KeyboardInterrupt:
        print("Zamykanie serwera proxy...")
        server_socket.close()

if __name__ == "__main__":
    main()
