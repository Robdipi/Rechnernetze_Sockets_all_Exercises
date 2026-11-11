import argparse
import base64
import getpass
import os
import socket
import ssl
from email.utils import formatdate, make_msgid

HOST = "asmtp.htwg-konstanz.de"
PORT = 587
TIMEOUT = 20


def _reply_complete(data):
    if not data.endswith(b"\r\n"):
        return False
    for line in data[:-2].split(b"\r\n"):
        if len(line) >= 4 and line[:3].isdigit() and line[3:4] == b" ":
            return True
    return False


def read_reply(sock):
    data = b""
    while not _reply_complete(data):
        chunk = sock.recv(4096)
        if not chunk:
            raise ConnectionError("connection closed by server")
        data += chunk
    return data.decode("utf-8", errors="replace")


def command(sock, line, expected=None):
    sock.sendall(line.encode("utf-8") + b"\r\n")
    reply = read_reply(sock)
    print(reply.rstrip())
    if expected is not None and not reply.startswith(expected):
        raise RuntimeError(f"expected {expected}, got {reply!r}")
    return reply


def build_message(mail_from, mail_to, subject, text):
    encoded_subject = base64.b64encode(subject.encode("utf-8")).decode("ascii")
    header = [
        f"From: {mail_from}",
        f"To: {mail_to}",
        f"Subject: =?utf-8?B?{encoded_subject}?=",
        f"Date: {formatdate(localtime=True)}",
        f"Message-ID: {make_msgid()}",
        "MIME-Version: 1.0",
        "Content-Type: text/plain; charset=utf-8",
        "Content-Transfer-Encoding: 8bit",
    ]
    lines = header + [""] + text.split("\n")
    stuffed = "\r\n".join("." + line if line.startswith(".") else line for line in lines)
    return (stuffed + "\r\n.\r\n").encode("utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default=os.environ.get("SMTP_USER", ""))
    parser.add_argument("--from", dest="mail_from", default=os.environ.get("MAIL_FROM", ""))
    parser.add_argument("--to", dest="mail_to", default=os.environ.get("MAIL_TO", ""))
    parser.add_argument("--subject", default="Testmail aus dem RN-Labor äöü")
    parser.add_argument("--text", default="Hallo,\ndies ist eine Testmail mit Umlauten: äöü.")
    args = parser.parse_args()

    password = os.environ.get("SMTP_PASSWORD") or getpass.getpass("SMTP password: ")
    mail_from = args.mail_from or args.user
    if not args.user or not args.mail_to:
        parser.error("--user and --to (or SMTP_USER and MAIL_TO) are required")

    with socket.create_connection((HOST, PORT), timeout=TIMEOUT) as raw:
        print(read_reply(raw).rstrip())
        command(raw, f"EHLO {socket.gethostname()}", "250")
        command(raw, "STARTTLS", "220")

        context = ssl.create_default_context()
        with context.wrap_socket(raw, server_hostname=HOST) as sock:
            command(sock, f"EHLO {socket.gethostname()}", "250")
            command(sock, "AUTH LOGIN", "334")
            command(sock, base64.b64encode(args.user.encode()).decode("ascii"), "334")
            command(sock, base64.b64encode(password.encode()).decode("ascii"), "235")
            command(sock, f"MAIL FROM:<{mail_from}>", "250")
            command(sock, f"RCPT TO:<{args.mail_to}>", "250")
            command(sock, "DATA", "354")
            sock.sendall(build_message(mail_from, args.mail_to, args.subject, args.text))
            print(read_reply(sock).rstrip())
            command(sock, "QUIT", "221")


if __name__ == "__main__":
    main()
