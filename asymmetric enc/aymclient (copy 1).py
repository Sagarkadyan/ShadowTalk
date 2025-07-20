import socket
import threading
import time
import rsa
import queue
from colorama import init, Fore, Style

# Initialize colorama
init()

# Constants
HEADER = 4
PORT = 9999
FORMAT = "utf-8"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

class EncryptedChatClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(ADDR)
        self.response_queue = queue.Queue()
        self.username = ""
        self.current_recipient = None
        self.running = True
        self.waiting_for_response = False
        
        # Generate keys on initialization
        self.pubkey, self.privkey = rsa.newkeys(512)
        with open("public.pem", "wb") as f:
            f.write(self.pubkey.save_pkcs1("PEM"))
        with open("private.pem", "wb") as f:
            f.write(self.privkey.save_pkcs1("PEM"))
        print(f"{Fore.GREEN}✅ Keys generated: public.pem, private.pem{Style.RESET_ALL}")

    def send_with_header(self, data):
        if isinstance(data, str):
            data = data.encode(FORMAT)
        self.client.send(str(len(data)).encode(FORMAT).ljust(HEADER))
        time.sleep(0.01)
        self.client.send(data)

    def recv_exact(self, num):
        data = b""
        while len(data) < num:
            chunk = self.client.recv(num - len(data))
            if not chunk:
                raise ConnectionError("Socket closed")
            data += chunk
        return data

    def receive_handler(self):
        while self.running:
            try:
                msg_type = self.recv_exact(3).decode(FORMAT)
                msg_len = int(self.recv_exact(HEADER).decode(FORMAT).strip())
                msg = self.recv_exact(msg_len)

                if msg_type == "MSG":
                    try:
                        decrypted = rsa.decrypt(msg, self.privkey).decode(FORMAT)
                        if ":" in decrypted:
                            sender, message = decrypted.split(":", 1)
                            self.print_message(sender, message)
                    except Exception as e:
                        print(f"\n{Fore.RED}[!] Failed to decrypt: {e}{Style.RESET_ALL}")
                        if self.current_recipient:
                            self.show_input_prompt()
                
                elif msg_type == "SYS":
                    sys_msg = msg.decode(FORMAT)
                    if not self.waiting_for_response:
                        print(f"\n{Fore.BLUE}[*] {sys_msg}{Style.RESET_ALL}")
                    if self.current_recipient:
                        self.show_input_prompt()
                    
                elif msg_type == "KEY":
                    self.response_queue.put((msg_type, msg))
                    
            except Exception as e:
                print(f"\n{Fore.RED}[Connection Error] {e}{Style.RESET_ALL}")
                self.running = False

    def print_message(self, sender, message):
        timestamp = time.strftime("%H:%M")
        if sender == self.username:
            color = Fore.CYAN
            sender_name = "You"
        else:
            color = Fore.MAGENTA
            sender_name = sender
            
        print(f"\n{color}[{timestamp}] {sender_name}: {message} 🔒{Style.RESET_ALL}")
        self.show_input_prompt()

    def show_input_prompt(self):
        if self.current_recipient:
            print(f"\nMessage to {self.current_recipient}: ", end="", flush=True)

    def send_message(self, recipient, message):
        self.waiting_for_response = True
        self.send_with_header(f"REQUESTKEY:{recipient}")
        
        try:
            msg_type, payload = self.response_queue.get(timeout=5)
            if msg_type == "KEY":
                their_key = rsa.PublicKey.load_pkcs1(payload)
                full_msg = f"{self.username}:{message}"
                encrypted = rsa.encrypt(full_msg.encode(FORMAT), their_key)
                payload_msg = f"SENDMSG:{recipient}".encode(FORMAT) + b":" + encrypted
                self.send_with_header(payload_msg)
                self.print_message(self.username, message)
                return True
            else:
                print(f"\n{Fore.RED}[!] {payload.decode(FORMAT)}{Style.RESET_ALL}")
                return False
        except queue.Empty:
            print(f"\n{Fore.RED}[!] No response from server{Style.RESET_ALL}")
            return False
        finally:
            self.waiting_for_response = False

    def clear_screen(self):
        print("\033[H\033[J", end="")

    def print_header(self):
        self.clear_screen()
        print(f"{Fore.YELLOW}🔐 Asymmetric Encrypted Chat{Style.RESET_ALL}")
        print(f"User: {self.username}")
        print("-" * 50)

    def graceful_exit(self):
        print(f"{Fore.YELLOW}\n[~] Disconnecting...{Style.RESET_ALL}")
        self.running = False
        self.send_with_header("disconnect")
        self.client.close()
        exit(0)

    def show_main_menu(self):
        print("\n1. Start chat")
        print("2. List online users")
        print("3. Exit")
        return input("Choose (1-3): ").strip()

    def select_recipient(self):
        self.send_with_header("LISTUSERS")
        print(f"{Fore.YELLOW}[~] Loading user list...{Style.RESET_ALL}")
        time.sleep(1)
        
        recipient = input("\nEnter recipient username: ").strip()
        if recipient.lower() == "back":
            return None
            
        self.current_recipient = recipient
        print(f"{Fore.GREEN}[✓] Now chatting with {recipient}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[~] Type '/back' to return to menu{Style.RESET_ALL}")
        return recipient

    def chat_loop(self):
        while self.running and self.current_recipient:
            try:
                print(f"Message to {self.current_recipient}: ", end="", flush=True)
                msg = input().strip()
                
                if msg.lower() == "/back":
                    self.current_recipient = None
                    return
                elif msg.lower() == "disconnect":
                    self.graceful_exit()
                
                if not self.send_message(self.current_recipient, msg):
                    self.current_recipient = None
                    
            except KeyboardInterrupt:
                print()
                self.graceful_exit()
            except Exception as e:
                print(f"\n{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")

    def run(self):
        try:
            self.print_header()
            self.username = input("Enter your username: ").strip()
            
            self.send_with_header(self.username)
            time.sleep(0.05)
            self.send_with_header(self.pubkey.save_pkcs1("PEM"))
            
            print(f"{Fore.GREEN}[+] Secure connection established{Style.RESET_ALL}")
            
            threading.Thread(target=self.receive_handler, daemon=True).start()
            
            while self.running:
                try:
                    choice = self.show_main_menu()
                    
                    if choice == "1":
                        if not self.current_recipient:
                            if not self.select_recipient():
                                continue
                        self.chat_loop()
                        
                    elif choice == "2":
                        self.send_with_header("LISTUSERS")
                        
                    elif choice == "3":
                        self.graceful_exit()
                        
                except KeyboardInterrupt:
                    self.graceful_exit()
                except Exception as e:
                    print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
                    
        except Exception as e:
            print(f"{Fore.RED}[!] Fatal error: {e}{Style.RESET_ALL}")
            self.graceful_exit()

if __name__ == "__main__":
    chat_client = EncryptedChatClient()
    chat_client.run()