import usocket as socket

def serve_forever(handler):
    s = socket.socket()

    # Binding to all interfaces - server will be accessible to other hosts!
    ai = socket.getaddrinfo("0.0.0.0", 80)
    print("Bind address info:", ai)
    addr = ai[0][-1]

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    print("Listening, connect your browser to http://<this_host>:80/")

    counter = 0
    while True:
        res = s.accept()
        client_sock = res[0]
        client_addr = res[1]
        print("Client address:", client_addr)
        print("Client socket:", client_sock)

        # .. but MicroPython socket objects support stream interface
        # directly, so calling .makefile() method is not required. If
        # you develop application which will run only on MicroPython,
        # especially on a resource-constrained embedded device, you
        # may take this shortcut to save resources.
        client_stream = client_sock

        print("Request:")
        req = client_stream.readline()
        print(req)
        while True:
            h = client_stream.readline()
            if h == b"" or h == b"\r\n":
                break
            print(h)
        response = handler(req)
        client_stream.write(response)
        client_stream.close()
        counter += 1
        print()

