import argparse
import socket
import threading

from protocol import RequestStream, calculate, pack_response

TIMEOUT = 10


def receive(conn):
    peer = conn.getpeername()
    print(f"{peer}: receive thread started")
    conn.settimeout(TIMEOUT)
    reader = RequestStream()
    try:
        while True:
            try:
                request = reader.read_request(conn)
            except socket.timeout:
                print(f"{peer}: {TIMEOUT}s without request, closing")
                return
            except OSError as exc:
                print(f"{peer}: {exc}")
                return
            if request is None:
                print(f"{peer}: closed by client")
                return
            request_id, operation, numbers = request
            try:
                result = calculate(operation, numbers)
            except (ValueError, OverflowError) as exc:
                print(f"{peer}: cannot calculate {operation}: {exc}")
                continue
            conn.sendall(pack_response(request_id, result))
            print(f"{peer}: id={request_id} {operation} N={len(numbers)} -> {result}")
    finally:
        conn.close()
        print(f"{peer}: receive thread stopped")


def listen(sock):
    while True:
        conn, addr = sock.accept()
        print(f"connection from {addr}")
        threading.Thread(target=receive, args=(conn,), daemon=True).start()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=50000)
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((args.host, args.port))
        server.listen()
        print(f"threaded TCP calculator listening on {args.host}:{args.port}")
        try:
            listen(server)
        except KeyboardInterrupt:
            print("\nstopped")


if __name__ == "__main__":
    main()
