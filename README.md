# Simple Python Web Server

## Project Overview

This project implements a simple web server in Python based on Greg Wilson's **“A Simple Web Server”** tutorial from the [500 Lines or Less](https://aosabook.org/en/500L/a-simple-web-server.html) book.  

The server supports:

- Serving static files from disk  
- Directory listings for directories without `index.html`  
- Running Python CGI scripts dynamically  
- Error handling for unknown paths or inaccessible files  

It demonstrates an understanding of HTTP, TCP/IP, sockets, and modular server design.

---

## Project Description

The main objectives achieved in this project:

- Understand the workflow of HTTP servers and how requests are processed  
- Serve static files and directories dynamically  
- Execute Python CGI scripts using a subprocess  
- Implement modular, extensible request handling using `base_case` and specialized handler classes  
- Generate structured HTML error pages for 404 and internal server exceptions  

---

## Features

1. **Static File Serving**  
   Serves files from the current working directory.  

2. **Directory Listing**  
   Displays directory contents when `index.html` is missing.  

3. **CGI Script Support**  
   Executes Python scripts and returns their output to the client.  

4. **Error Handling**  
   Returns an HTML page with an error message when a file or directory is missing or inaccessible.  

5. **Extensible Architecture**  
   Request handling is modular and supports adding new case handlers easily.  

---

 