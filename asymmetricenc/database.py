import sqlite3

# Connect (creates the database file if it doesn't exist)
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Create table

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    cypher_text TEXT
)
''')
conn.commit()

# Demonstration: Insert a sample user (in production, hash the password!)
name = "saar"
email = "le@xiimpjjiole.com"
password = "up_oonjjseure_password"   # Replace with a hash in production!
cypher_text = "ECl=]]PTED_MESAGE_HERE"
new_passwd="saar12,"
def adder(name,email,password,cypher_text):
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password, cypher_text) VALUES (?, ?, ?, ?)",
            (name, email, password, cypher_text)
        )
        conn.commit()
        return("Inserted successfully!")
    except sqlite3.IntegrityError:
        return("Email already exists.")


def password(name):
    try:
        cursor.execute(
            "SELECT password FROM users WHERE name = ?", (name,)
        )
        result=cursor.fetchone()
        if result:
            return(result[0])
        else :
            return("user does not exist")    
        
    except:
        return("error")   

def update_pss(name, new_passwd):
    try:
        cursor.execute(
            "UPDATE users SET password = ? WHERE name = ?",
            (new_passwd, name)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return "user does not exist"
        else:
            return "password updated successfully"
    except Exception as e:
        return f"error: {e}"

def key_req(name):
    try:
        cursor.execute(
            "SELECT cypher_text FROM users WHERE name = ?", (name,)
        
        )
        result=cursor.fetchone()
        return(result)
    except:
        return("user does not exist ")
if __name__== "__main__":
    conn.close()
