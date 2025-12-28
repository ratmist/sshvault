import paramiko
import sys
import threading
import msvcrt
import time


def connect_ssh(host: str, port: int, user: str, password: str):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect(
        hostname=host,
        port=port,
        username=user,
        password=password,
        timeout=10,
        look_for_keys=False,
        allow_agent=False,
    )

    channel = client.invoke_shell()
    channel.settimeout(0.0)

    print("Connected. Interactive shell started. Ctrl+C to exit.\n")

    def recv_loop():
        while True:
            try:
                if channel.recv_ready():
                    data = channel.recv(4096)
                    if not data:
                        break
                    sys.stdout.write(data.decode(errors="ignore"))
                    sys.stdout.flush()
            except Exception:
                break
            time.sleep(0.01)

    recv_thread = threading.Thread(target=recv_loop, daemon=True)
    recv_thread.start()

    try:
        while True:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()

                if ch == "\r":
                    channel.send("\n")
                elif ch == "\x03":  
                    break
                else:
                    channel.send(ch)

            time.sleep(0.01)

    except KeyboardInterrupt:
        pass
    finally:
        channel.close()
        client.close()
        print("\nConnection closed")
