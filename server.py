import http.server
import os

# ----------------------------------------------------------------------
# Custom Exception for Server Errors
# ----------------------------------------------------------------------
class ServerException(Exception):
    """
    Custom exception for internal server errors.
    Raised when a file is missing or an unknown object is requested.
    """
    pass

# ----------------------------------------------------------------------
# Base Case Handler
# ----------------------------------------------------------------------
class base_case:
    """
    Abstract parent class for handling different request scenarios (cases).
    Subclasses implement test() to check if the case applies
    and act() to execute the appropriate response.
    """

    def handle_file(self, handler, full_path):
        """
        Serve the contents of a file to the client.

        :param handler: The RequestHandler instance
        :param full_path: Full path of the file to serve
        """
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            handler.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(full_path, msg)
            handler.handle_error(msg)

    def test(self, handler):
        """
        Check if this case applies. Must be implemented in subclasses.

        :param handler: The RequestHandler instance
        :return: Boolean
        """
        raise NotImplementedError('Subclasses must implement test()')

    def act(self, handler):
        """
        Execute the action associated with this case. Must be implemented in subclasses.

        :param handler: The RequestHandler instance
        """
        raise NotImplementedError('Subclasses must implement act()')

# ----------------------------------------------------------------------
# Specific Case Handlers
# ----------------------------------------------------------------------
class case_no_file(base_case):
    """
    Case when the requested path does not exist.
    """

    def test(self, handler):
        """
        Returns True if the file or directory does not exist.
        """
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        """
        Raise a ServerException indicating that the file was not found.
        """
        raise ServerException("'{0}' not found".format(handler.path))

class case_existing_file(base_case):
    """
    Case when the requested path exists and is a file.
    """

    def test(self, handler):
        """
        Returns True if the requested path is an existing file.
        """
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        """
        Serve the file contents to the client.
        """
        self.handle_file(handler, handler.full_path)

class case_always_fail(base_case):
    """
    Fallback case if no other case applies.
    """

    def test(self, handler):
        """
        Always returns True, making this the final fallback.
        """
        return True

    def act(self, handler):
        """
        Raise a ServerException indicating an unknown object.
        """
        raise ServerException("Unknown object '{0}'".format(handler.path))

# ----------------------------------------------------------------------
# Main Request Handler
# ----------------------------------------------------------------------
class RequestHandler(http.server.BaseHTTPRequestHandler):
    """
    HTTP request handler using the Case system.

    Requests are evaluated against a list of case handlers in order.
    The first case whose test() returns True is executed with act().
    """

    # List of case handlers (order matters)
    Cases = [case_no_file(),
             case_existing_file(),
             case_always_fail()]

    # HTML template for error pages
    Error_Page = """\
        <html>
            <body>
                <h1>Error accessing {path}</h1>
                <p>{msg}</p>
            </body>
        </html>
        """

    def do_GET(self):
        """
        Handle GET requests.

        Determines the full path requested and iterates through Cases.
        Executes the first applicable case.
        """
        try:
            # Full filesystem path of the requested resource
            self.full_path = os.getcwd() + self.path

            # Evaluate each case in order
            for case in self.Cases:
                if case.test(self):
                    case.act(self)
                    break

        except Exception as msg:
            # Handle all errors using the custom error page
            self.handle_error(msg)

    def handle_error(self, msg):
        """
        Send an HTML error response to the client.

        :param msg: Error message string
        """
        content = self.Error_Page.format(path=self.path, msg=msg).encode('utf-8')
        self.send_content(content, 404)

    def send_content(self, content, status=200):
        """
        Send HTTP response headers and content.

        :param content: Byte content to send
        :param status: HTTP status code (default 200)
        """
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

# ----------------------------------------------------------------------
# Main Server Loop
# ----------------------------------------------------------------------
if __name__ == '__main__':
    serverAddress = ('', 8080)  # Bind to all interfaces on port 8080
    print("Server (Refactored) started on http://localhost:8080 ...")
    server = http.server.HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()
