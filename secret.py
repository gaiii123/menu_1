import os
import secrets

# Generate a 32-character hexadecimal secret key
secret_key = secrets.token_hex(32)
print(secret_key)