import socket
import selectors 
import types 
from fnmatch import fnmatch
import sys

sel = selectors.DefaultSelector()

queues = [[] for i in range(3)]
ptrs = [0] * 3

# implements call-and-response protocol: refer to README for details
def handle_command(request, data):
    """
    Handles incoming commands from the client.
    """
    print(f"received request: [{request}]")

    args = request.split(' ')
    match args[0]:
        case "login":
            id = int(args[1])
            data.id = id 
            queues[id] = []
            ptrs[id] = 0
            return "success"
        case "send":
            y = int(args[1])
            msg = args[2]
            queues[y].append(msg)
            return "success"
        case "size":
            return str(len(queues[data.id]) - ptrs[data.id])
        case "pop":
            if ptrs[data.id] == len(queues[data.id]):
                return "error"
            ptrs[data.id] += 1
            return queues[data.id][ptrs[data.id] - 1]
        case _:
            return "error: invalid command"

def accept_wrapper(sock):
    """
    Accepts new connections
    """
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"", id=-1)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE 
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    """
    Services existing connections and reads/writes to the connected socket
    """
    sock = key.fileobj
    data = key.data 
    return_data = ""
    
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb += recv_data
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            return_data = handle_command(data.outb.decode("utf-8"), data)
            return_data = return_data.encode("utf-8")
            sent = sock.send(return_data)
            data.outb = b""


def main():
    # Note: we know this is bad practice, but since this code is only meant as a toy experiment we
    #       decided there's no point in making host and port command line arguments
    host = "127.0.0.1"
    port = 5544
    
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((host, port))
    lsock.listen()
    print("Listening on", (host, port))
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data = None)
    try:
        while True:
            events = sel.select(timeout = None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()


if __name__ == "__main__":
    main()