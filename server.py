import http.server  # Provides the base classes for implementing an HTTP server
import os           # File system operations: paths, directories, checking existence
import subprocess   # For executing external scripts (CGI support)
import sys          # Access to Python runtime (used for subprocess)

# ----------------------------------------------------------------------
# Custom Exception
# ----------------------------------------------------------------------
class ServerException(Exception):
    """
    Custom exception class for internal server errors.
    Raised when a request cannot be handled properly.
    """
    pass

# ----------------------------------------------------------------------
# Base Case Handler
# ----------------------------------------------------------------------
class base_case(object):
    """
    Abstract parent class for all request handling cases.
    Defines the interface and helper methods for child case handlers.
    """
    
    def handle_file(self, handler, full_path):
        """
        Reads a file from disk and sends it as an HTTP response.
        
        Args:
            handler: instance of RequestHandler
            full_path: absolute path to the requested file
        """
        try:
            with open(full_path, 'rb') as reader:  # Open file in binary mode
                content = reader.read()
            handler.send_content(content)
        except IOError as msg:
            # If file cannot be read, generate a formatted error
            msg = "'{0}' cannot be read: {1}".format(full_path, msg)
            handler.handle_error(msg)

    def index_path(self, handler):
        """
        Returns the path to index.html for a directory.
        """
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        """
        Abstract method to determine if this case applies.
        Must be overridden by child classes.
        """
        assert False, 'Not implemented.'

    def act(self, handler):
        """
        Abstract method to perform the action if test() passes.
        Must be overridden by child classes.
        """
        assert False, 'Not implemented.'

# ----------------------------------------------------------------------
# Specific Case Handlers
# ----------------------------------------------------------------------
class case_no_file(base_case):
    """Handles requests where the requested path does not exist."""
    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))


class case_cgi_file(base_case):
    """Handles Python scripts (.py) executed as CGI."""
    def test(self, handler):
        # Only applies if file exists and has .py extension
        return os.path.isfile(handler.full_path) and handler.full_path.endswith('.py')

    def act(self, handler):
        # Execute the script as a subprocess and send output
        handler.run_cgi(handler.full_path)


class case_existing_file(base_case):
    """Handles requests for normal files (HTML, CSS, etc.)"""
    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        self.handle_file(handler, handler.full_path)


class case_directory_index_file(base_case):
    """Handles directories containing an index.html file."""
    def test(self, handler):
        return os.path.isdir(handler.full_path) and os.path.isfile(self.index_path(handler))

    def act(self, handler):
        self.handle_file(handler, self.index_path(handler))


class case_directory_no_index_file(base_case):
    """Handles directories without an index.html file (listing)."""
    def test(self, handler):
        return os.path.isdir(handler.full_path) and not os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.list_dir(handler.full_path)


class case_always_fail(base_case):
    """Fallback case if no other case matches (catch-all)."""
    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknown object '{0}'".format(handler.path))

# ----------------------------------------------------------------------
# Main Request Handler
# ----------------------------------------------------------------------
class RequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Main handler class for HTTP GET requests.
    Uses the Case system to determine how to handle requests.
    """

    # Order matters: first matching case is executed
    Cases = [
        case_no_file(),
        case_cgi_file(),          # CGI must precede regular file handling
        case_existing_file(),
        case_directory_index_file(),
        case_directory_no_index_file(),
        case_always_fail()
    ]

    # Templates for error pages and directory listings
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

    # ------------------------------------------------------------------
    # Request Handling
    # ------------------------------------------------------------------
    def do_GET(self):
        """
        Handles GET requests. Determines the requested path,
        and delegates processing to the first matching Case.
        """
        try:
            self.full_path = os.getcwd() + self.path  # Absolute path of request
            for case in self.Cases:
                if case.test(self):
                    case.act(self)
                    break
        except Exception as msg:
            self.handle_error(msg)

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------
    def list_dir(self, full_path):
        """
        Generates a directory listing page for folders without index.html.
        """
        try:
            entries = os.listdir(full_path)
            bullets = ['<li>{0}</li>'.format(e) for e in entries if not e.startswith('.')]
            page = self.Listing_Page.format('\n'.join(bullets), path=self.path)
            self.send_content(page.encode('utf-8'))
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
            self.handle_error(msg)

    def run_cgi(self, full_path):
        """
        Executes a Python script (.py) and sends its output.
        """
        try:
            data = subprocess.check_output([sys.executable, full_path])
            self.send_content(data)
        except Exception as msg:
            msg = "'{0}' cannot be executed: {1}".format(self.path, msg)
            self.handle_error(msg)

    def handle_error(self, msg):
        """
        Sends a formatted 404 error page.
        """
        content = self.Error_Page.format(path=self.path, msg=msg).encode('utf-8')
        self.send_content(content, 404)

    def send_content(self, content, status=200):
        """
        Sends content to the client with headers.
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
    print("Server (With CGI Support) started on http://localhost:8080 ...")
    server = http.server.HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()
