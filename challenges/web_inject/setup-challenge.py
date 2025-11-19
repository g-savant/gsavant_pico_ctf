import json
import os
import secrets
import string

FLAG_PATH = "/challenge/flag"
ADMIN_PASS_PATH = "/challenge/admin_password"
METADATA_PATH = "/challenge/metadata.json"


def random_password():
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(24))


def main():
    flag = os.environ.get("FLAG", "picoCTF{dev_flag}").strip()
    admin_password = random_password()

    os.makedirs("/challenge", exist_ok=True)
    with open(FLAG_PATH, "w") as fh:
        fh.write(flag)
    with open(ADMIN_PASS_PATH, "w") as fh:
        fh.write(admin_password)
    with open(METADATA_PATH, "w") as fh:
        json.dump({"flag": flag}, fh)


if __name__ == "__main__":
    main()
