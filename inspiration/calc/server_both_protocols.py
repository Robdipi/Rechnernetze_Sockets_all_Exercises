import argparse
import socket
import threading


def tcp_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        print(f"TCP echo listening on {host}:{port}")
        while True:
            conn, peer = server.accept()
            with conn:
                data = conn.recv(65536)
                conn.sendall(b"TCP: " + data)
                print(f"TCP {peer}: {data!r}")


def udp_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((host, port))
        print(f"UDP echo listening on {host}:{port}")
        while True:
            data, peer = sock.recvfrom(65535)
            sock.sendto(b"UDP: " + data, peer)
            print(f"UDP {peer}: {data!r}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=50000)
    args = parser.parse_args()

    threading.Thread(target=tcp_server, args=(args.host, args.port), daemon=True).start()
    udp_server(args.host, args.port)


if __name__ == "__main__":
    main()
