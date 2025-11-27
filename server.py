import http.server
import os

# ----------------------------------------------------------------------
# Custom Exception for Server Errors
# ----------------------------------------------------------------------
class ServerException(Exception):
    """
    Custom exception for internal server errors.
    Raised when a file or directory cannot be accessed or is unknown.
    """
    pass

# ----------------------------------------------------------------------
# Base Case Handler
# ----------------------------------------------------------------------
class base_case:
    """
    Abstract parent class for request scenario handlers.
    Subclasses implement test() to check if the case applies,
    and act() to execute the correct response.
    """

    def handle_file(self, handler, full_path):
        """
        Serve a file to the client.

        :param handler: RequestHandler instance
        :param full_path: Full filesystem path of the file
        """
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            handler.send_content(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(full_path, msg)
            handler.handle_error(msg)

    def index_path(self, handler):
        """
        Return the path of index.html inside a directory.

        :param handler: RequestHandler instance
        :return: Full path to index.html
        """
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        """
        Determine if this case applies. Must be overridden.
        """
        raise NotImplementedError('Subclasses must implement test()')

    def act(self, handler):
        """
        Execute the action for this case. Must be overridden.
        """
        raise NotImplementedError('Subclasses must implement act()')

# ----------------------------------------------------------------------
# Specific Case Handlers
# ----------------------------------------------------------------------
class case_no_file(base_case):
    """Case for non-existent files or directories."""

    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))

class case_existing_file(base_case):
    """Case for existing files."""

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        self.handle_file(handler, handler.full_path)

class case_directory_index_file(base_case):
    """Case for directories containing an index.html file."""

    def test(self, handler):
        return os.path.isdir(handler.full_path) and os.path.isfile(self.index_path(handler))

    def act(self, handler):
        self.handle_file(handler, self.index_path(handler))

class case_directory_no_index_file(base_case):
    """Case for directories without an index.html, serve directory listing."""

    def test(self, handler):
        return os.path.isdir(handler.full_path) and not os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.list_dir(handler.full_path)

class case_always_fail(base_case):
    """Fallback case if no other cases apply."""

    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknown object '{0}'".format(handler.path))

# ----------------------------------------------------------------------
# Main Request Handler
# ----------------------------------------------------------------------
class RequestHandler(http.server.BaseHTTPRequestHandler):
    """
    HTTP request handler using the Case system.
    Requests are evaluated in order; first case to pass test() is executed.
    """

    # List of cases in order of evaluation
    Cases = [
        case_no_file(),
        case_existing_file(),
        case_directory_index_file(),
        case_directory_no_index_file(),
        case_always_fail()
    ]

    # Templates
    Error_Page = """\
        <html>
        <body>
            <h1>Error accessing {path}</h1>
            <p>{msg}</p>
        </body>
        </html>
        """
    Listing_Page = """\
        <html>
        <body>
            <h1>Listing for {path}</h1>
            <ul>
                {0}
            </ul>
        </body>
        </html>
        """

    def do_GET(self):
        """
        Handle GET requests.
        Evaluates each case in order until a match is found.
        """
        try:
            self.full_path = os.getcwd() + self.path
            for case in self.Cases:
                if case.test(self):
                    case.act(self)
                    break
        except Exception as msg:
            self.handle_error(msg)

    def list_dir(self, full_path):
        """
        Generate an HTML directory listing for folders without index.html.

        :param full_path: Full path of the directory
        """
        try:
            entries = os.listdir(full_path)
            # Filter hidden files and create list items
            bullets = ['<li><a href="{0}">{0}</a></li>'.format(e) 
                       for e in entries if not e.startswith('.')]
            page = self.Listing_Page.format('\n'.join(bullets), path=self.path)
            self.send_content(page.encode('utf-8'))
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
            self.handle_error(msg)

    def handle_error(self, msg):
        """
        Send an error response page.

        :param msg: Error message
        """
        content = self.Error_Page.format(path=self.path, msg=msg).encode('utf-8')
        self.send_content(content, 404)

    def send_content(self, content, status=200):
        """
        Send HTTP response with headers and content.

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
    serverAddress = ('', 8080)
    print("Server (With Directory Listing) started on http://localhost:8080 ...")
    server = http.server.HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()
