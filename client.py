import socket
import ssl
import threading
import os
import platform

HOST = "10.30.203.149"  
PORT = 5556

def open_file(filename):
    try:
        if platform.system() == "Darwin":  # Mac
            os.system(f"open {filename}")
        elif platform.system() == "Windows":
            os.system(f"start {filename}")
    except:
        pass

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(4096)

            if not data:
                break

            # FILE RECEIVE
            if data.startswith(b"/file"):
                parts = data.decode().split()
                filename = parts[1]
                size = int(parts[2])

                file_data = b""

                while len(file_data) < size:
                    chunk = sock.recv(4096)
                    file_data += chunk

                save_name = "received_" + filename

                with open(save_name, "wb") as f:
                    f.write(file_data)

                print(f"\nReceived file: {save_name}")

                # AUTO OPEN
                open_file(save_name)

            else:
                print(data.decode())

        except:
            print("Disconnected from server")
            break

def start_client():
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    secure_sock = context.wrap_socket(sock, server_hostname=HOST)

    secure_sock.connect((HOST, PORT))

    threading.Thread(target=receive_messages, args=(secure_sock,), daemon=True).start()

    while True:
        msg = input()

        # EXIT
        if msg == "/exit":
            secure_sock.send(b"/exit")
            secure_sock.close()
            break

        # SEND FILE
        if msg.startswith("/sendfile"):
            parts = msg.split()

            if len(parts) < 2:
                print("Usage: /sendfile filename")
                continue

            filename = parts[1]

            try:
                with open(filename, "rb") as f:
                    data = f.read()

                header = f"/file {filename} {len(data)}\n"
                secure_sock.sendall(header.encode())
                secure_sock.sendall(data)

                print(f"File '{filename}' sent")

            except:
                print("File not found")

            continue

        # NORMAL / COMMANDS
        secure_sock.send(msg.encode())

if __name__ == "__main__":
    start_client()
