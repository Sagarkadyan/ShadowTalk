import os
import sys
import random
import string
from pathlib import Path

KEY_FILE = Path("random_word.txt")
suffix ="eedeeeefrgklnlkn"
def generate_random_word(length=2):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_or_create_word():
    if KEY_FILE.exists():
        with open(KEY_FILE, 'r') as f:
            word = f.read().strip()
    else:
        word = generate_random_word()
        with open(KEY_FILE, 'w') as f:
            f.write(word)
    return word

def main():
    if len(sys.argv) != 2:
        print("Usage: python shared_key_generator.py <suffix>")
       
    
    
    word = get_or_create_word()
    shared_key = word + suffix

    print(f"Your random word: {word}")
    print(f"Your suffix: {suffix}")
    print(f"Shared key: {shared_key}")

if __name__ == "__main__":
    main()