import socket


class TCPServer:
    """Base server class for handling TCP connections.
    The HTTP server will inherit from this class.
    """

    def __init__(self, host="127.0.0.1", port=8888):
        self.host = host
        self.port = port

    def start(self):
        """Method for starting the server"""

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(5)

        print("Listening at", s.getsockname())

        while True:
            conn, addr = s.accept()
            print("Connected by", addr)

            # For the sake of this,
            # we're reading just the first 1024 bytes sent by the client.
            data = conn.recv(1024)

            response = self.handle_request(data)

            conn.sendall(response)
            conn.close()

    def handle_request(self, data):
        """Handles incoming data and returns a response.
        Override this in subclass.
        """
        return data


class HTTPServer(TCPServer):
    """The actual HTTP server class."""

    headers = {
        "Server": "NoobServer",
        "Content-Type": "text/html",
    }

    status_codes = {
        200: "OK",
        404: "Not Found",
        501: "Not Implemented",
    }

    def handle_request(self, data):
        """Handles incoming requests"""

        request = HTTPRequest(data)  # Get a parsed HTTP request

        try:
            # Call the corresponding handler method for the current
            # request's method
            handler = getattr(self, "handle_%s" % request.method)
        except AttributeError:
            handler = self.HTTP_501_handler

        response = handler(request)
        return response
