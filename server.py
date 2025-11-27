"""
A minimal HTTP server exposing request metadata.

This module provides a simple HTTP server using Python's built-in
`http.server` library. It dynamically returns an HTML page containing
details about the client request. The script is designed for educational,
debugging, and demonstration purposes rather than production deployment.
"""

import http.server
import time


class RequestHandler(http.server.BaseHTTPRequestHandler):
    """
    A basic HTTP request handler that returns an HTML page showing
    request information such as the client address, command, and path.
    """

    Page = """\
<html>
<body>
    <h1>Simple Python Web Server</h1>
    <p>This page is generated dynamically by Python.</p>
    <table border="1">
        <tr><td>Header</td><td>Value</td></tr>
        <tr><td>Date and time</td><td>{date_time}</td></tr>
        <tr><td>Client host</td><td>{client_host}</td></tr>
        <tr><td>Client port</td><td>{client_port}</td></tr>
        <tr><td>Command</td><td>{command}</td></tr>
        <tr><td>Path</td><td>{path}</td></tr>
    </table>
</body>
</html>
"""

    def do_GET(self):
        """
        Handle HTTP GET requests.

        The method constructs an HTML page with request metadata and
        sends it to the client with a 200 OK response.
        """
        page = self.create_page()
        self.send_page(page)

    def create_page(self):
        """
        Populate the HTML template with request-specific values.

        Returns:
            str: A fully formatted HTML page.
        """
        values = {
            "date_time": self.date_time_string(),
            "client_host": self.client_address[0],
            "client_port": self.client_address[1],
            "command": self.command,
            "path": self.path,
        }
        return self.Page.format(**values)

    def send_page(self, page):
        """
        Send the HTTP headers and the HTML payload.

        Args:
            page (str): The HTML content to send.
        """
        encoded = page.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()

        self.wfile.write(encoded)


if __name__ == "__main__":
    """
    Entry point for running the server.

    The server listens on port 8080 and handles requests using the
    RequestHandler class. This configuration is suitable for local
    development and testing, not for production workloads.
    """
    server_address = ("", 8080)
    print("Starting server on http://localhost:8080 ...")
    server = http.server.HTTPServer(server_address, RequestHandler)
    server.serve_forever()
