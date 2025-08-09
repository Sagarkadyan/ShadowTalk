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
name = "sa"
email = "e@xiimjjiole.com"
password = "up_njjseure_password"   # Replace with a hash in production!
cypher_text = "l=]]PTED_MESAGE_HERE"
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

#hi=adder(name,email,password,cypher_text)
#print(hi)
def check_password(cursor, name, user_password):
    try:
        cursor.execute(
            "SELECT password FROM users WHERE name = ?", (name,)
        )
        row = cursor.fetchone()
        if row is None:
            return "user not found"
        stored_password = row[0]
        if stored_password == user_password:
            return "correct pass"
        else:
            return "wrong pass"
    except Exception as e:
        return f"invalid pass: {e}"

hj=check_password(cursor,name,password)
print(hj)
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
