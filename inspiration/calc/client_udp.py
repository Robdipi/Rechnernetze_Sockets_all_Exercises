import argparse
import socket

from protocol import RESPONSE_SIZE, UDP_MAX_N, pack_request, unpack_response

TIMEOUT = 10


def build_requests():
    return [
        (1, "SUM", [1, 2, 3, 4, 5]),
        (2, "PRO", [2, 3, 4, 5]),
        (3, "MIN", [9, -4, 7, 0]),
        (4, "MAX", [9, -4, 7, 0]),
        (5, "SUM", list(range(1, UDP_MAX_N + 1))),
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=50000)
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(TIMEOUT)
        print(f"local socket: {sock.getsockname()}")
        for request_id, operation, numbers in build_requests():
            payload = pack_request(request_id, operation, numbers)
            sock.sendto(payload, (args.host, args.port))
            data, peer = sock.recvfrom(RESPONSE_SIZE)
            response_id, result = unpack_response(data)
            if response_id != request_id:
                raise ValueError(f"expected id {request_id}, got {response_id}")
            print(f"id={request_id} {operation} N={len(numbers)} -> {result} (from {peer})")


if __name__ == "__main__":
    main()
