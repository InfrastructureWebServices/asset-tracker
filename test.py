# import secrets
# print(secrets.token_hex(3))
import uuid

uuid_str = "4f3f3cae-1829-4a20-be24-de831f2c7b1e"

new = uuid.UUID(uuid_str)
print(new.hex)