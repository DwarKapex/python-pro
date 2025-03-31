import threading
import time

import pytest
import requests
from web_server import HOST, PORT, start_server


@pytest.fixture(scope="module")
def server():
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    time.sleep(1)  # start delay
    yield


def test_index_page(server):
    response = requests.get(f"http://{HOST}:{PORT}/", timeout=1)
    assert response.status_code == 200
    assert "index.html" in response.text


def test_not_found_page(server):
    response = requests.get(f"http://{HOST}:{PORT}/noexist_page.html", timeout=1)
    assert response.status_code == 404
    assert "File Not Found" in response.text
