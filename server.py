import http.server
import os

class RequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Custom HTTP request handler to serve files from the local directory
    and display a friendly error page if a file is missing or inaccessible.
    """

    # Template for the HTML error page
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
        Determine whether the requested path is a file, exists, or triggers an error.
        """
        try:
            # Construct the full path to the requested resource
            full_path = os.getcwd() + self.path

            if not os.path.exists(full_path):
                # File or path does not exist
                self.handle_error(f"'{self.path}' not found")
            elif os.path.isfile(full_path):
                # Requested path is a file; serve it
                self.handle_file(full_path)
            else:
                # Path exists but is not a file (e.g., directory); return error
                self.handle_error(f"Unknown object '{self.path}'")

        except Exception as msg:
            # Catch-all for unexpected exceptions
            self.handle_error(msg)

    def handle_file(self, full_path):
        """
        Serve the requested file content.
        Opens the file in binary mode and sends it to the client.
        """
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            self.send_content(content)
        except IOError as msg:
            # If the file cannot be read, send an error page
            msg = f"'{self.path}' cannot be read: {msg}"
            self.handle_error(msg)

    def handle_error(self, msg):
        """
        Generate and send a friendly HTML error page with a 404 status.
        """
        content = self.Error_Page.format(path=self.path, msg=msg).encode('utf-8')
        self.send_content(content, 404)

    def send_content(self, content, status=200):
        """
        Send HTTP response headers and content to the client.
        :param content: Byte content of the response
        :param status: HTTP status code (default: 200)
        """
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

#----------------------------------------------------------------------

if __name__ == '__main__':
    # Server configuration
    serverAddress = ('', 8080)  # '' means bind to all available interfaces
    print("Serving files from current directory on http://localhost:8080 ...")

    # Instantiate the HTTP server with the custom handler
    server = http.server.HTTPServer(serverAddress, RequestHandler)

    # Run the server indefinitely
    server.serve_forever()
