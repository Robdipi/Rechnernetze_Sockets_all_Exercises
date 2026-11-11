import argparse
import socket

from protocol import ByteStream, RESPONSE_SIZE, pack_request, unpack_response

TIMEOUT = 10


def build_requests():
    return [
        (101, "SUM", [1, 2, 3, 4, 5]),
        (102, "PRO", [2, 3, 4, 5]),
        (103, "MIN", [9, -4, 7, 0]),
        (104, "MAX", [9, -4, 7, 0]),
        (105, "SUM", list(range(1, 20001))),
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=50000)
    args = parser.parse_args()

    requests = build_requests()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(TIMEOUT)
        sock.connect((args.host, args.port))
        payload = b"".join(pack_request(*request) for request in requests)
        print(f"sending {len(requests)} requests in one sendall ({len(payload)} bytes)")
        sock.sendall(payload)

        reader = ByteStream()
        results = {}
        for _ in requests:
            data = reader.read(sock, RESPONSE_SIZE)
            if data is None:
                raise ConnectionError("server closed the connection")
            response_id, result = unpack_response(data)
            results[response_id] = result

    for request_id, operation, numbers in requests:
        print(f"id={request_id} {operation} N={len(numbers)} -> {results[request_id]}")


if __name__ == "__main__":
    main()
