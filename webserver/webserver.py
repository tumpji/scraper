import http.server
import socketserver
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Generator, List

import database

import psycopg2
import logging

logger = logging.getLogger("webserver")

@dataclass
class Ad:
    title: str
    image_urls: List[str]  # = field(hash=False)


class MockDB:
    def gather_responses(self) -> Generator[Ad, None, None]:
        a = r"https://d18-a.sdn.cz/d_18/c_img_QL_J7/z6vdQB.jpeg?fl=res,400,300,3|shr,,20|jpg,90"
        b = r"https://d18-a.sdn.cz/d_18/c_img_QL_J7/z6vdQB.jpeg?fl=res,400,300,3|shr,,20|jpg,90"
        c = r"https://d18-a.sdn.cz/d_18/c_img_QP_LA/ZhBBJ9.jpeg?fl=res,400,300,3|shr,,20|jpg,90"

        yield Ad('First Ad', [a])
        yield Ad('Second Ad', [a, a])
        yield Ad('Third Ad', [b, c])
        yield Ad('Third Ad', [b, c, b, c, b, c])
        yield Ad('+ěščřžýáíé Ad', [b, c, b, b, b, b, b, b, b, b, b])


class SrealityHandler(http.server.SimpleHTTPRequestHandler, MockDB):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def write(self, content: str):
        self.wfile.write(content.encode('utf-8'))

    @contextmanager
    def tag(self, tagtype: str):
        self.write(f'<{tagtype}>')
        try:
            yield None
        finally:
            self.write(f'</{tagtype}>')

    def simple_tag(self, tagtype: str, **kwargs):
        self.write(f"<{tagtype} ")
        for k, v in kwargs.items():
            self.write(f'{k}="{v}" ')
        self.write(">")

    def do_GET(self):
        db_connection = None
        try:
            db_connection = database.Connection()
            elements = db_connection.select_table()
        except Exception as e:
            logger.critical(e, exc_info=True)
            self.send_error(500, "Error Establishing a Database Connection")
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            with self.tag('h1'):
                self.write("Sreality ads:")
            for title, url in elements:
                with self.tag('div'):
                    with self.tag('h2'):
                        self.write(title)
                self.simple_tag('img', src=url, style="padding:5px;width:400px;height:300;")
        finally:
            if db_connection is not None:
                db_connection.close()


if __name__ == "__main__":
    PORT = 8080

    Handler = SrealityHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
