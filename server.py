import socket
import os
import mimetypes
import json


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

    def response_line(self, status_code):
        """Returns response line (as bytes)"""
        reason = self.status_codes.get(status_code, "Unknown Status Code")
        response_line = "HTTP/1.1 %s %s\r\n" % (status_code, reason)

        return response_line.encode()

    def response_headers(self, extra_headers=None):
        """Returns headers (as bytes).

        The `extra_headers` can be a dict for sending
        extra headers with the current response
        """
        headers_copy = self.headers.copy()  # make a local copy of headers

        if extra_headers:
            headers_copy.update(extra_headers)

        headers = ""

        for h in headers_copy:
            headers += "%s: %s\r\n" % (h, headers_copy[h])

        return headers.encode()  # convert str to bytes

    def handle_OPTIONS(self, request):
        """Handler for OPTIONS HTTP method"""

        response_line = self.response_line(200)

        extra_headers = {"Allow": "OPTIONS, GET"}
        response_headers = self.response_headers(extra_headers)

        blank_line = b"\r\n"

        return b"".join([response_line, response_headers, blank_line])

    def handle_GET(self, request):
        """Handler for GET HTTP method"""

        path = request.uri.strip("/")  # remove slash from URI

        if not path:
            # If path is empty, that means user is at the homepage
            # so just serve index.html
            path = "htdocs/index.html"

        if os.path.exists(path) and not os.path.isdir(path):  # don't serve directories
            response_line = self.response_line(200)

            # find out a file's MIME type
            # if nothing is found, just send `text/html`
            content_type = mimetypes.guess_type(path)[0] or "text/html"

            extra_headers = {"Content-Type": content_type}
            response_headers = self.response_headers(extra_headers)

            with open(path, "rb") as f:
                response_body = f.read()
        else:
            response_line = self.response_line(404)
            response_headers = self.response_headers()
            response_body = b"<h1>404 Not Found</h1>"

        blank_line = b"\r\n"

        response = b"".join(
            [response_line, response_headers, blank_line, response_body]
        )

        return response

    def handle_POST(self, request):
        """Handler for POST HTTP method"""

        # Access the request body to get POST data
        post_data = request.body.decode("utf-8")

        try:
            # Try to parse the POST data as JSON
            json_data = json.loads(post_data)

            # Process and handle the json_data as needed
            response_body = f"Received JSON data: {json_data}"

            content_type = "application/json"
        except json.JSONDecodeError:
            # Handle JSON decoding error
            # Assume it's HTML form data in this case
            response_body = f"Received HTML form data: {post_data}"

            content_type = "text/html"

        response_line = self.response_line(200)
        extra_headers = {"Content-Type": content_type}
        response_headers = self.response_headers(extra_headers)

        blank_line = b"\r\n"

        if isinstance(response_body, str):
            response_body = response_body.encode()

        response = b"".join(
            [response_line, response_headers, blank_line, response_body]
        )

        return response

    def HTTP_501_handler(self, request):
        """Returns 501 HTTP response if the requested method hasn't been implemented."""

        response_line = self.response_line(status_code=501)

        response_headers = self.response_headers()

        blank_line = b"\r\n"

        response_body = b"<h1>501 Not Implemented</h1>"

        return b"".join([response_line, response_headers, blank_line, response_body])


class HTTPRequest:
    """Parser for HTTP requests.

    It takes raw data and extracts meaningful information about the incoming request.

    Instances of this class have the following attributes:

        `self.method`: The current HTTP request method sent by the client (string)
        `self.uri`: URI for the current request (string)
        `self.http_version`: HTTP version used by the client (string)
        `self.headers`: Dictionary containing the HTTP headers
        `self.body`: The body of the HTTP request (bytes)
    """

    def __init__(self, data):
        self.method = None
        self.uri = None
        self.http_version = "1.1"
        self.headers = {}
        self.body = b""

        self.parse(data)

    def parse(self, data):
        lines = data.split(b"\r\n")

        request_line = lines[0]
        words = request_line.split(b" ")

        self.method = words[0].decode()

        if len(words) > 1:
            self.uri = words[1].decode()

        if len(words) > 2:
            self.http_version = words[2]

        # Parse headers
        for line in lines[1:]:
            if not line:
                break
            header, value = line.split(b":", 1)
            self.headers[header.strip().decode()] = value.strip()

        # Parse request body
        body_start = data.find(b"\r\n\r\n") + 4
        self.body = data[body_start:]


if __name__ == "__main__":
    server = HTTPServer()
    server.start()
