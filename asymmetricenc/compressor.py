import requests

# Create a session object
session = requests.Session()

# Log in and maintain the session automatically
login_url = "http://10.201.110.70/"
credentials = {"username": "note", "password": passwd}
for i in 
response = session.post(login_url, data=credentials)

if "Welcome" in response.text:
    print("[+] Login successful. Session cookies are stored automatically!")
else:
    print("[-] Login failed.")
