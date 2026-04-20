# 🔐 Secure Multi-Client Chat System (Python + SSL)

A secure multi-client chat application built using Python sockets and SSL encryption.
This system supports chat rooms, private messaging, file transfer, and admin controls.

Team members: 
1. Neha Sachin - PES1UG24CS296
2. Mutnuri Nagavalli Sri Sravya - PES1UG24CS284
3. Nishitha Sathish - PES1UG24CS304
---

## 🚀 Features

* 🔒 SSL/TLS encrypted communication
* 👥 Multiple chat rooms (create/join)
* 💬 Real-time messaging
* 📩 Private messaging using SRN
* 📂 File transfer between clients
* 👑 Admin controls (kick users)
* 📜 View active users in a room

---

## 🛠️ Technologies Used

* Python 3
* `socket` (network communication)
* `ssl` (secure encryption)
* `threading` (multi-client handling)

---

## 📁 Project Structure

```
.
├── server.py
├── client.py
├── cert.pem
├── key.pem
├── generate_cert.py
├── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

---

### 2. Generate SSL Certificates

If not already present:

```bash
python generate_cert.py
```

This will create:

* `cert.pem`
* `key.pem`

---

### 3. Start the Server

```bash
python server.py
```

Server will run on:

```
HOST = 0.0.0.0
PORT = 5556
```

---

### 4. Start the Client

Update the `HOST` in `client.py` to your server IP:

```python
HOST = "YOUR_SERVER_IP"
```

Then run:

```bash
python client.py
```

---

## 💡 Usage

### 🏠 Room Options

* Create a new room
* Join an existing room

---

### 💬 Commands

| Command                | Description            |
| ---------------------- | ---------------------- |
| `/exit`                | Leave the chat         |
| `/users`               | Show users in room     |
| `/msg <SRN> <message>` | Send private message   |
| `/kick <username>`     | Kick user (admin only) |
| `/sendfile <filename>` | Send file              |

---

### 📂 File Transfer

* Send file:

  ```
  /sendfile example.pdf
  ```
* Received files are saved as:

  ```
  received_<filename>
  ```

---

## 🔐 Security Notes

* Uses SSL encryption but disables certificate verification on client side (`CERT_NONE`)
* Suitable for learning/demo purposes
* For production:

  * Enable certificate verification
  * Use trusted certificates

---

## ⚠️ Limitations

* No persistent storage (rooms reset on server restart)
* Basic authentication (name + SRN only)
* No GUI (CLI-based)

---

## 📌 Future Improvements

* Add database support
* GUI interface (Tkinter / Web)
* Strong authentication system
* File progress tracking
* End-to-end encryption

---
