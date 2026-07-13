import pytest
from playwright.sync_api import sync_playwright
import threading
import http.server
import socketserver
import time
import socket
import os

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

PORT = get_free_port()

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve from the root directory of the project
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        super().__init__(*args, directory=root_dir, **kwargs)

def start_server(port):
    with socketserver.TCPServer(("", port), Handler) as httpd:
        httpd.serve_forever()

@pytest.fixture(scope="session")
def server():
    thread = threading.Thread(target=start_server, args=(PORT,), daemon=True)
    thread.start()

    # Wait until the port is open
    start_time = time.time()
    while time.time() - start_time < 5:
        try:
            with socket.create_connection(("localhost", PORT), timeout=1):
                break
        except OSError:
            time.sleep(0.1)
    else:
        raise RuntimeError(f"Server did not start on port {PORT}")

    yield

@pytest.fixture(scope="session")
def browser_context():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        yield context
        browser.close()

def test_get_arabic_name(server, browser_context):
    page = browser_context.new_page()
    page.goto(f"http://localhost:{PORT}/index.html")

    page.wait_for_load_state("domcontentloaded")

    test_cases = [
        ("بيتزا | Pizza", "بيتزا"),
        ("شاورما دجاج | Chawarma Poulet", "شاورما دجاج"),
        ("بيتزا | Pizza (M)", "بيتزا (M)"),
        ("لحم | Viande (500g)", "لحم (500g)"),
        ("عصير | Jus (1L)", "عصير (1L)"),
        ("بيتزا", "بيتزا"),
        ("Pizza", "Pizza"),
        (" بيتزا  |  Pizza  ", "بيتزا"),
        ("بيتزا | Pizza | Piza (L)", "بيتزا"),
        ("بيتزا | Pizza (M) Extra", "بيتزا"),
        (" | ", ""),
    ]

    for input_name, expected in test_cases:
        result = page.evaluate("function(name) { return getArabicName(name); }", input_name)
        assert result == expected, f"Failed for '{input_name}': expected '{expected}', but got '{result}'"
