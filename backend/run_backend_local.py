import errno
import socket

import uvicorn


def _patched_socketpair(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0):
    if family not in (socket.AF_INET, socket.AF_INET6):
        raise ValueError("Only AF_INET and AF_INET6 are supported")
    if type != socket.SOCK_STREAM:
        raise ValueError("Only SOCK_STREAM is supported")
    if proto != 0:
        raise ValueError("Only protocol zero is supported")

    host = "127.0.0.1" if family == socket.AF_INET else "::1"
    last_error = None

    for port in range(45000, 45100):
        listener = socket.socket(family, type, proto)
        client = socket.socket(family, type, proto)
        try:
            listener.bind((host, port))
            listener.listen(1)
            client.connect((host, port))
            server, _ = listener.accept()
            return server, client
        except OSError as exc:
            last_error = exc
            client.close()
            listener.close()
            if exc.errno in {errno.EADDRINUSE, errno.EACCES, 10013, 10048}:
                continue
            raise
        finally:
            listener.close()

    raise last_error or OSError("No se pudo crear socketpair local")


socket.socketpair = _patched_socketpair


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
