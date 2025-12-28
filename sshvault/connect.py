import paramiko
import sys
import threading
import time
import os

# Windows-only
if os.name == "nt":
    import msvcrt
else:
    import select


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

    # ---- Receive loop (same for all platforms) ----
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

    threading.Thread(target=recv_loop, daemon=True).start()

    try:
        while True:
            # -------- Windows --------
            if os.name == "nt":
                if msvcrt.kbhit():
                    ch = msvcrt.getwch()

                    if ch == "\r":
                        channel.send("\n")
                    elif ch == "\x03":  # Ctrl+C
                        break
                    else:
                        channel.send(ch)

            # -------- macOS / Linux --------
            else:
                r, _, _ = select.select([sys.stdin], [], [], 0.05)
                if r:
                    data = sys.stdin.read(1)
                    if not data:
                        break
                    channel.send(data)

            time.sleep(0.01)

    except KeyboardInterrupt:
        pass
    finally:
        channel.close()
        client.close()
        print("\nConnection closed")
