msg = "hardik:hi"

username="hardik"
if ":" in msg:
    recipient, actual_msg = msg.split(":", 1)
hi = username+":"+actual_msg
print(msg)
print(len(hi))