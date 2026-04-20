import socket
import ssl
import threading

HOST = '0.0.0.0'
PORT = 5556

rooms = {}  
room_locks = {}

# PRINT ALL ROOMS (SERVER SIDE)
def print_rooms():
    print("\nActive Chat Rooms:")
    if not rooms:
        print("No active rooms")
    else:
        for room, data in rooms.items():
            users = [f"{n}({s})" for (_, n, s) in data["users"]]
            print(f"{room} → {len(users)} users → {users}")
    print()

#BROADCAST
def broadcast(room, message, sender):
    with room_locks[room]:
        for client, _, _ in rooms[room]["users"][:]:
            if client != sender:
                try:
                    client.send(message)
                except:
                    client.close()
                    rooms[room]["users"] = [(c, n, s) for (c, n, s) in rooms[room]["users"] if c != client]

#PRIVATE MESSAGE
def send_private(room, sender_name, sender_srn, target_srn, message):
    for client, name, srn in rooms[room]["users"]:
        if srn == target_srn:
            try:
                client.send(f"[PRIVATE] {sender_name}({sender_srn}): {message}\n".encode())
                return True
            except:
                return False
    return False

#HANDLE CLIENT
def handle_client(conn):
    name, srn, room = "", "", ""
    try:
        conn.send(b"1. Create Room\n2. Join Room\nChoice: ")
        choice = conn.recv(1024).decode().strip()

        #CREATE ROOM
        if choice == "1":
            conn.send(b"Enter room name: ")
            room = conn.recv(1024).decode().strip()

            if room in rooms:
                conn.send(b"Room already exists\n")
                return

            rooms[room] = {"users": [], "admin": None}
            room_locks[room] = threading.Lock()
            conn.send(b"Room created\n")

        #JOIN ROOM
        elif choice == "2":
            if not rooms:
                conn.send(b"No rooms available\n")
                return

            room_list = "\n".join(rooms.keys())
            conn.send(f"Available rooms:\n{room_list}\nEnter room: ".encode())

            room = conn.recv(1024).decode().strip()

            if room not in rooms:
                conn.send(b"Invalid room\n")
                return

        else:
            return

        #NAME + SRN (AND)
        while True:
            conn.send(b"Enter name: ")
            name = conn.recv(1024).decode().strip()

            conn.send(b"Enter SRN: ")
            srn = conn.recv(1024).decode().strip()

            if any(name == n and srn == s for (_, n, s) in rooms[room]["users"]):
                conn.send(b"User already exists\n")
            else:
                break

        #ADMIN
        if rooms[room]["admin"] is None:
            rooms[room]["admin"] = srn
            conn.send(b"You are admin\n")

        rooms[room]["users"].append((conn, name, srn))

        print(f"[JOIN] {name}({srn}) → {room}")
        print_rooms()

        conn.send(f"Joined {room}\n".encode())
        broadcast(room, f"{name}({srn}) joined\n".encode(), conn)

        #LOOP
        while True:
            message = conn.recv(4096)
            if not message:
                break

            #FILE
            if message.startswith(b"/file"):
                header = message.decode()
                _, filename, size = header.split()
                size = int(size)

                data = b""
                while len(data) < size:
                    data += conn.recv(4096)

                print(f"[FILE] {name} sent {filename}")

                for client, _, _ in rooms[room]["users"]:
                    if client != conn:
                        client.send(f"/file {filename} {size}".encode())
                        client.send(data)
                continue

            decoded = message.decode().strip()

            #EXIT
            if decoded == "/exit":
                print(f"[EXIT] {name}({srn})")
                broadcast(room, f"{name}({srn}) left\n".encode(), conn)
                break

            #USERS
            if decoded == "/users":
                users = [f"{n}({s})" for (_, n, s) in rooms[room]["users"]]
                conn.send(f"{', '.join(users)}\n".encode())
                continue

            #PRIVATE
            if decoded.startswith("/msg"):
                parts = decoded.split(" ", 2)
                if len(parts) < 3:
                    conn.send(b"Usage: /msg SRN message\n")
                    continue

                target_srn, msg = parts[1], parts[2]

                print(f"[PRIVATE] {name} → {target_srn}: {msg}")

                if send_private(room, name, srn, target_srn, msg):
                    conn.send(b"Sent\n")
                else:
                    conn.send(b"SRN not found\n")

                continue

            #KICK (ADMIN + SERVER)
            if decoded.startswith("/kick"):
                parts = decoded.split()
                if len(parts) < 2:
                    continue

                target = parts[1]

                # allow server OR admin
                if rooms[room]["admin"] != srn:
                    conn.send(b"Only admin can kick\n")
                    continue

                for client, n, s in rooms[room]["users"]:
                    if n == target:
                        client.send(b"You were kicked\n")
                        client.close()

                        rooms[room]["users"] = [(c, n2, s2) for (c, n2, s2) in rooms[room]["users"] if c != client]

                        broadcast(room, f"{target} kicked\n".encode(), conn)
                        print(f"[KICK] {target}")
                        break

                continue

            #NORMAL
            print(f"[ROOM {room}] {name}({srn}): {decoded}")
            broadcast(room, f"{name}({srn}): {decoded}".encode(), conn)

    except Exception as e:
        print("Error:", e)

    finally:
        conn.close()

        for r in rooms:
            rooms[r]["users"] = [(c, n, s) for (c, n, s) in rooms[r]["users"] if c != conn]

        print(f"[DISCONNECT] {name}")
        print_rooms()

#SERVER
def start_server():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind((HOST, PORT))
    s.listen(5)

    print(f"Server running on {HOST}:{PORT}")

    while True:
        c, addr = s.accept()
        secure = context.wrap_socket(c, server_side=True)

        print(f"[NEW] {addr}")
        threading.Thread(target=handle_client, args=(secure,)).start()

if __name__ == "__main__":
    start_server()
