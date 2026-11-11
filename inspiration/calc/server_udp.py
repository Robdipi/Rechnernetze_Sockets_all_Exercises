import argparse
import socket

from protocol import calculate, pack_response, unpack_request

MAX_DATAGRAM = 65535


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=50000)
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((args.host, args.port))
        print(f"UDP calculator listening on {args.host}:{args.port}")
        try:
            while True:
                data, peer = sock.recvfrom(MAX_DATAGRAM)
                try:
                    request_id, operation, numbers = unpack_request(data)
                    result = calculate(operation, numbers)
                except (ValueError, OverflowError) as exc:
                    print(f"{peer}: bad request: {exc}")
                    continue
                sock.sendto(pack_response(request_id, result), peer)
                print(f"{peer}: id={request_id} {operation} N={len(numbers)} -> {result}")
        except KeyboardInterrupt:
            print("\nstopped")


if __name__ == "__main__":
    main()
