import struct

HEADER_FORMAT = "!I3sH"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
RESPONSE_FORMAT = "!Ii"
RESPONSE_SIZE = struct.calcsize(RESPONSE_FORMAT)
OPERATIONS = ("SUM", "PRO", "MIN", "MAX")
UDP_MAX_N = 16374


def pack_request(request_id, operation, numbers):
    op = operation.encode("utf-8")
    if operation not in OPERATIONS or len(op) != 3:
        raise ValueError(f"unknown operation: {operation!r}")
    if not 0 <= len(numbers) <= 0xFFFF:
        raise ValueError("number count out of range for unsigned short")
    header = struct.pack(HEADER_FORMAT, request_id, op, len(numbers))
    body = struct.pack(f"!{len(numbers)}i", *numbers) if numbers else b""
    return header + body


def unpack_request(data):
    if len(data) < HEADER_SIZE:
        raise ValueError("datagram shorter than request header")
    request_id, op, count = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
    expected = HEADER_SIZE + 4 * count
    if len(data) != expected:
        raise ValueError(f"expected {expected} bytes, got {len(data)}")
    numbers = list(struct.unpack(f"!{count}i", data[HEADER_SIZE:])) if count else []
    return request_id, op.decode("utf-8"), numbers


def pack_response(request_id, result):
    return struct.pack(RESPONSE_FORMAT, request_id, result)


def unpack_response(data):
    return struct.unpack(RESPONSE_FORMAT, data)


def calculate(operation, numbers):
    if operation == "SUM":
        return sum(numbers)
    if operation == "PRO":
        result = 1
        for number in numbers:
            result *= number
        return result
    if operation == "MIN":
        return min(numbers)
    if operation == "MAX":
        return max(numbers)
    raise ValueError(f"unknown operation: {operation!r}")


class RequestStream:
    def __init__(self):
        self.buffer = bytearray()

    def _fill(self, sock, size):
        while len(self.buffer) < size:
            chunk = sock.recv(65536)
            if not chunk:
                return False
            self.buffer.extend(chunk)
        return True

    def read_request(self, sock):
        if not self._fill(sock, HEADER_SIZE):
            return None
        request_id, op, count = struct.unpack(HEADER_FORMAT, self.buffer[:HEADER_SIZE])
        total = HEADER_SIZE + 4 * count
        if not self._fill(sock, total):
            return None
        body = bytes(self.buffer[HEADER_SIZE:total])
        del self.buffer[:total]
        numbers = list(struct.unpack(f"!{count}i", body)) if count else []
        return request_id, op.decode("utf-8"), numbers


class ByteStream:
    def __init__(self):
        self.buffer = bytearray()

    def read(self, sock, size):
        while len(self.buffer) < size:
            chunk = sock.recv(65536)
            if not chunk:
                return None
            self.buffer.extend(chunk)
        data = bytes(self.buffer[:size])
        del self.buffer[:size]
        return data
