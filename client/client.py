import socket
import os

# Ruta base para los archivos del cliente
FILEPATH = "/app/client_files"

def upload_file(client_socket, filename):
    # Verifica si el archivo existe en la ruta especificada
    filepath = os.path.join(FILEPATH, filename)
    if os.path.isfile(filepath):
        filesize = os.path.getsize(filepath)
        client_socket.send(f'UPLOAD == {filename} == {filesize}'.encode())
        confirm = client_socket.recv(1048576).decode()
        print(confirm)
        if confirm.startswith('Valid'):
            with open(filepath, 'rb') as f:
                data = f.read(1048576)
                while data:
                    client_socket.send(data)
                    data = f.read(1048576)

            response = client_socket.recv(1048576).decode()
            print(response)
    else:
        print(f"File not found: {filepath}")

def search_file(client_socket, file_name, file_type):
    client_socket.send(f'SEARCH == {file_name} == {file_type}'.encode())
    response = client_socket.recv(1048576).decode()
    # Después de recibir un archivo o un resultado, enviar un ACK al servidor
    client_socket.send(b'ACK')
    if response.startswith('FOUND'):
        num_files = int(response.split()[1])
        search_results = {}
        for _ in range(num_files):
            result = client_socket.recv(1048576).decode()
            name = result.split(" == ")[0]
            id = result.split(" == ")[1]
            search_results[name] = id
            print(f"Found: {name}")
            client_socket.send(b'ACK')
        command = input("Enter command (DOWNLOAD, RETURN): ")
        if command == 'DOWNLOAD':
            name = input("Enter the name of the file to download: ")
            download_file(client_socket, search_results[name])

        elif command != 'RETURN':
            print("Invalid command. Please try again.")
    else:
        print("No files found")

def download_file(client_socket, id):
    client_socket.send(f'DOWNLOAD == {id}'.encode())
    response = client_socket.recv(1048576).decode()
    if response.startswith('FileSize'):
        filesize = int(response.split()[1])
        download_path = os.path.join(FILEPATH, 'downloaded_' + id)
        with open(download_path, 'wb') as f:
            bytes_received = 0
            while bytes_received < filesize:
                data = client_socket.recv(1048576)
                f.write(data)
                bytes_received += len(data)
        print(f"Download complete: {download_path}")
    else:
        print("File not found on server.")

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('10.0.11.2', 5000))  # Conecta al servidor en la red configurada
        print("Connected to server")
    except socket.error as e:
        print(f"Error connecting to server: {e}")
        return

    while True:
        command = input("Enter command (UPLOAD, SEARCH, EXIT): ")
        if command.startswith('UPLOAD'):
            filename = input("Enter the name of the file to upload: ")
            upload_file(client_socket, filename)
        elif command.startswith('SEARCH'):
            filename = input("Enter file name: ")
            file_type = input("Enter file type: ")
            search_file(client_socket, filename, file_type)
        elif command == 'EXIT':
            client_socket.send(b'EXIT')
            client_socket.close()
            print("Disconnected from server")
            break
        else:
            print("Invalid command. Please try again.")

if __name__ == '__main__':
    main()