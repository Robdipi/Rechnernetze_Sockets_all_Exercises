import argparse
import socket

from protocol import ByteStream, RESPONSE_SIZE, pack_request, unpack_response

TIMEOUT = 10


def build_requests():
    return [
        (1, "SUM", [1, 2, 3, 4, 5]),
        (2, "PRO", [2, 3, 4, 5]),
        (3, "MIN", [9, -4, 7, 0]),
        (4, "MAX", [9, -4, 7, 0]),
        (5, "SUM", list(range(1, 20001))),
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=50000)
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(TIMEOUT)
        print(f"connecting to {args.host}:{args.port}")
        sock.connect((args.host, args.port))
        print(f"local socket: {sock.getsockname()}, remote socket: {sock.getpeername()}")

        reader = ByteStream()
        for request_id, operation, numbers in build_requests():
            sock.sendall(pack_request(request_id, operation, numbers))
            data = reader.read(sock, RESPONSE_SIZE)
            if data is None:
                raise ConnectionError("server closed the connection")
            response_id, result = unpack_response(data)
            if response_id != request_id:
                raise ValueError(f"expected id {request_id}, got {response_id}")
            print(f"id={request_id} {operation} N={len(numbers)} -> {result}")


if __name__ == "__main__":
    main()
