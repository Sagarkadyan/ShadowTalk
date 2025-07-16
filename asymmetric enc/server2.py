
        while True:
            msg_len = int(recv_exact(conn, HEADER).decode(FORMAT).strip())
            msg = recv_exact(conn, msg_len)

            if msg.startswith(b"REQUESTKEY:"):
                recipient = msg.decode(FORMAT).split(":")[1]
                if recipient in client_keys:
                    conn.send(b"KEY")
                    send_with_header(conn, client_keys[recipient])
                else:
                    conn.send(b"SYS")
                    send_with_header(conn, "User not found")

            elif msg.startswith(b"SENDMSG:"):
                parts = msg.split(b":", 2)
                recipient = parts[1].decode(FORMAT)
                encrypted = parts[2]
                if recipient in clients:
                    clients[recipient].send(b"MSG")
                    send_with_header(clients[recipient], encrypted)

                    conn.send(b"SYS")
                    send_with_header(conn, "Message delivered")
                else:
                    conn.send(b"SYS")
                    send_with_header(conn, "Recipient not online")

            elif msg.decode(FORMAT).strip() == "disconnect":
                break

    except Exception as e:
        print(f"[ERR] {username}: {e}")
    finally:
        if username:
            clients.pop(username, None)
            client_keys.pop(username, None)
        conn.close()
        print(f"[-] {username} disconnected")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()
print(f"[Server] Listening on {SERVER}:{PORT}")
while True:
    conn, addr = server.accept()
    threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
