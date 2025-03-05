import socket 
import sys
import random
import time

host = "127.0.0.1"
port = 5544

def query(s, request):
    s.sendall(request.encode("utf-8"))
    return s.recv(1024).decode('utf-8')

def main():
    s0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s0.connect((host, port))
    assert(query(s0, "login 0") == "success")

    s1.connect((host, port))
    assert(query(s1, "login 1") == "success")

    s2.connect((host, port))
    assert(query(s2, "login 2") == "success")

    assert(query(s1, "send 0 100") == "success")
    assert(query(s0, "size") == "1")
    assert(query(s1, "size") == "0")

    assert(query(s2, "send 0 200") == "success")
    assert(query(s0, "size") == "2")
    assert(query(s1, "size") == "0")

    assert(query(s0, "pop") == "100")
    assert(query(s0, "size") == "1")
    assert(query(s0, "pop") == "200")
    assert(query(s0, "size") == "0")

    print("all tests passed!")

if __name__ == "__main__":
    main()
