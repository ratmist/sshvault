import argparse
import random
import pyfiglet
from getpass import getpass
from vault import Vault
from connect import connect_ssh

BANNER = r"""
███████╗███████╗██╗  ██╗██╗   ██╗ █████╗ ██╗   ██╗██╗  ████████╗
██╔════╝██╔════╝██║  ██║██║   ██║██╔══██╗██║   ██║██║  ╚══██╔══╝
███████╗███████╗███████║██║   ██║███████║██║   ██║██║     ██║ 
╚════██║╚════██║██╔══██║██║   ██║██╔══██║██║   ██║██║     ██║
███████║███████║██║  ██║╚██████╔╝██║  ██║╚██████╔╝███████╗██║
╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝

SSH Vault v0.1.0
Author : ratmist
GitHub : https://github.com/ratmist
"""


def print_banner():
    print(BANNER.rstrip())
    print()


def add_new_service(vault: Vault):
    name = input("Service name: ")
    host = input("Host: ")
    port = int(input("Port: "))
    user = input("User: ")
    password = getpass("Password: ")

    vault.add_service(
        name=name,
        service={
            "host": host,
            "port": port,
            "user": user,
            "passwd": password
        }
    )
    vault.save()

    print(f"Service '{name}' added\n")

def del_service(vault: Vault, name: str):
    vault.del_service(name)
    vault.save()

    print(f"Service '{name}' deleted\n")

def conn_to_service(vault: Vault, name: str):
    if name not in vault.services:
        print("Service not found")
        return

    service = vault.services[name]

    print(f"Connecting to {name}...\n")

    connect_ssh(
        host=service["host"],
        port=service["port"],
        user=service["user"],
        password=service["passwd"]
    )

def edit_service(vault: Vault, name: str):
    svc = vault.services.get(name)
    if not svc:
        print("Service not found")
        return

    print("Leave empty to keep current value")

    user = input(f"User [{svc['user']}]: ") or svc["user"]
    password = getpass("Password [hidden]: ") or svc["passwd"]

    vault.update_service(name, user=user, passwd=password)
    vault.save()
    print("Service updated")

def shell_mode():
    print_banner()
    master_password = getpass("Master password: ")

    try:
        vault = Vault.open_or_create(master_password)
    except Exception:
        print("Invalid master password")
        return

    print("sshvault interactive shell. Type 'help' or 'exit'.")

    while True:
        try:
            cmd = input("sshvault> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not cmd:
            continue

        if cmd in ("exit", "quit"):
            break

        elif cmd == "help":
            print(
                "Commands:\n"
                "  list\n"
                "  add\n"
                "  del <name>\n"
                "  connect <name>\n"
                "  exit"
            )

        elif cmd == "list":
            if not vault.services:
                print("No services")
            else:
                for name, svc in vault.services.items():
                    print(
                        f"- {name} "
                        f"({svc['user']}@{svc['host']}:{svc['port']})"
                    )

        elif cmd == "add":
            add_new_service(vault)

        elif cmd.startswith("delete "):
            _, name = cmd.split(maxsplit=1)
            del_service(vault, name)

        elif cmd.startswith("connect "):
            _, name = cmd.split(maxsplit=1)
            conn_to_service(vault, name)
        elif cmd.startswith("edit "):
            _, name = cmd.split(maxsplit=1)
            edit_service(vault, name)
        else:
            print("Unknown command")

def main():
    parser = argparse.ArgumentParser(
        prog="sshvault",
        description="Encrypted SSH connection manager"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="initialize new vault")
    subparsers.add_parser("list", help="list all services")
    subparsers.add_parser("add", help="add new service")

    delete = subparsers.add_parser("del", help="delete service")
    delete.add_argument("name")

    edit = subparsers.add_parser("edit", help="edit service")
    edit.add_argument("name")

    connect = subparsers.add_parser("connect", help="connect to service")
    connect.add_argument("name")

    subparsers.add_parser("shell", help="interactive shell (unlock once)")

    args = parser.parse_args()
    if args.command != "shell":
        print_banner()
    if args.command == "shell":
        shell_mode()
        return

    if args.command == "init":
        if Vault.exists():
            print("Vault already initialized")
            return

        pw1 = getpass("Create master password: ")
        pw2 = getpass("Confirm master password: ")

        if pw1 != pw2:
            print("Passwords do not match")
            return

        Vault.open_or_create(pw1)
        print("Vault initialized")
        return

    if not Vault.exists():
        print("Vault not initialized. Run `sshvault init` first.")
        return

    master_password = getpass("Master password: ")

    try:
        vault = Vault.open_or_create(master_password)
    except Exception:
        print("Invalid master password")
        return

    if args.command == "list":
        if not vault.services:
            print("Please add one service")
        else:
            for name, service in vault.services.items():
                host = service["host"]
                port = service["port"]
                user = service["user"]

                print(f"- {name} ({user}@{host}:{port})")

    elif args.command == "add":
        add_new_service(vault)

    elif args.command == "del":
        del_service(vault, args.name)

    elif args.command == "edit":
        edit_service(vault, args.name)

    elif args.command == "connect":
        conn_to_service(vault, args.name)

# def main():
#     parser = argparse.ArgumentParser(
#         prog="sshvault",
#         description="Encrypted SSH connection manager"
#     )

#     subparsers = parser.add_subparsers(
#         dest="command",
#         required=True
#     )

#     subparsers.add_parser("init", help="initialize new vault")
#     subparsers.add_parser("list", help="list all services")
#     subparsers.add_parser("add", help="add new service")

#     delete = subparsers.add_parser("delete", help="delete service")
#     delete.add_argument("name", help="service name")

#     connect = subparsers.add_parser("connect", help="connect to service")
#     connect.add_argument("name", help="service name")

#     edit = subparsers.add_parser("edit", help="edit service")
#     edit.add_argument("name", help="service name")


#     subparsers.add_parser("shell", help="interactive shell (unlock once)")
#     args = parser.parse_args()
    
#     if args.command == "init":
#         if Vault.exists():
#             print("Vault already initialized")
#             return

#         pw1 = getpass("Create master password: ")
#         pw2 = getpass("Confirm master password: ")

#         if pw1 != pw2:
#             print("Passwords do not match")
#             return

#         Vault.open_or_create(pw1)
#         print("Vault initialized")
#         return
#     try:
#         vault = Vault.open_or_create(master_password)
#     except Exception:
#         print("Invalid master password")
#         return
    
#     if not Vault.exists():
#         print("Vault not initialized. Run `sshvault init` first.")
#         return

#     master_password = getpass("Master password: ")

    
    
#     if args.command == "list":
        # if not vault.services:
        #     print("Please add one service")
        # else:
        #     for name, service in vault.services.items():
        #         host = service["host"]
        #         port = service["port"]
        #         user = service["user"]

        #         print(f"- {name} ({user}@{host}:{port})")

#     elif args.command == "add":
#         add_new_service(vault)

#     elif args.command == "delete":
#         del_service(vault, args.name)

#     elif args.command == "connect":
#         conn_to_service(vault, args.name)
#     elif args.command == "edit":
#         edit_service(vault, args.name)
#     elif args.command == "passwd":
#         old = getpass("Old master password: ")
#         new1 = getpass("New master password: ")
#         new2 = getpass("Confirm new master password: ")

#         if new1 != new2:
#             print("Passwords do not match")
#             return

#         vault.change_master_password(old, new1)
#         print("Master password updated")
#     if args.command == "shell":
#         shell_mode()
#         return
if __name__ == "__main__":
    main()
