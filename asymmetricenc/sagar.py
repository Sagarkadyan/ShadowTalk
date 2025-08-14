def recv_exact(conn, msg_len):
    """
    Receives exactly msg_len bytes from the socket.
    """
    chunks = []
    bytes_recd = 0
    while bytes_recd < msg_len:
        chunk = conn.recv(min(msg_len - bytes_recd, 2048))
        if chunk == b'':
            raise RuntimeError("Socket connection broken")
        chunks.append(chunk)
        bytes_recd = bytes_recd + len(chunk)
    return b''.join(chunks)

# ... (The rest of your code) ...

# Inside the handle_client function where you receive the data
try:
    header_bytes = conn.recv(8)  # Assuming the header is 8 bytes
    if not header_bytes:
        # Client disconnected
        return
    msg_len = int.from_bytes(header_bytes, 'big')
    
    data_bytes = recv_exact(conn, msg_len)
    data_str = data_bytes.decode('utf-8')
    data = json.loads(data_str)
    # ... (process the data) ...

except (json.JSONDecodeError, RuntimeError) as e:
    # Handle the specific errors here
    print(f"Error during data reception/decoding: {e}")