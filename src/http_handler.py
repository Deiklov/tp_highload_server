import asyncio
import mimetypes
import socket
from email.utils import formatdate
from datetime import datetime
from logging import log
from time import mktime
import os
from urllib import parse
from src.config import Config


class Methods:
    Get = 'GET'
    Head = 'HEAD'


MIME_TYPES = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.swf': 'application/x-shockwave-flash',
}

STATUS_CODES = {
    200: 'OK',
    403: 'FORBIDDEN',
    404: 'NOT_FOUND',
    405: 'METHOD_NOT_ALLOWED'
}

allowed_methods = ['GET', 'HEAD']

headers = {
    'Server': 'python_non_blocking_server',
    'Date': '',
    'Connection': '',
    'Content-Length': '',
    'Content-Type': ''
}


def guess_mime_type(filename):
    return mimetypes.guess_type(filename)


class Response:
    def __init__(self, config: Config, method: str = 'GET', protocol: str = 'HTTP/1.1', status: int = 200,
                 path_to_file: [str, None] = None):
        self.config = config
        self.method = method
        self.protocol = protocol
        self.status = status
        self.headers = {'Connection': 'close', 'Server': 'tpserver',
                        'Date': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}
        self.path_to_file = path_to_file
        self.raw = None
        self.max_socket_size = self.config.buff_size
        if self.path_to_file is not None:
            self.add_mime_headers()

    def add_mime_headers(self):
        file_size = os.path.getsize(self.path_to_file)
        mime_type, _ = mimetypes.guess_type(self.path_to_file)
        self.headers.update({'Content-Type': mime_type})
        self.headers.update({'Content-Length': file_size})

    async def send(self, loop: asyncio.AbstractEventLoop, conn: socket.socket = None):
        await loop.sock_sendall(conn, self.raw if self.raw is not None else self.format())
        if self.path_to_file is not None and self.method != 'HEAD':
            with open(self.path_to_file, 'rb') as f:
                batch = f.read(self.max_socket_size)
                try:
                    while len(batch) > 0:
                        await loop.sock_sendall(conn, batch)
                        batch = f.read(self.max_socket_size)
                except BrokenPipeError:
                    pass

    def format(self) -> bytes:
        self.raw = f'{self.protocol} {self.status} {STATUS_CODES[self.status]}\r\n'
        self.raw += '\r\n'.join([f'{k}: {v}' for k, v in self.headers.items()]) + '\r\n\r\n'
        self.raw = self.raw.encode('utf-8')
        return self.raw


class Request:
    DELIMITER = '\r\n'
    HEADERS_DELIMITER = ': '
    INDEX_FILE = 'index.html'
    ALLOWED_METHODS = ['GET', 'HEAD']

    def __init__(self, raw, config=None):
        self.method = None
        self.protocol = None
        self.url = None
        self._parse_request(raw)
        self.config = config

    def _parse_request(self, raw: str):
        parts = raw.split(self.DELIMITER)
        try:
            self.method, self.url, self.protocol = parts[0].split(' ')
            self.url = parse.unquote(self.url)
            if '?' in self.url:
                self.url = self.url[:self.url.index('?')]
        except ValueError:
            pass

    async def validate_request(self):
        # check thar method is allowed
        if self.method not in allowed_methods:
            return Response(self.config, status=405)
        #
        if '/../' in self.url:
            return Response(self.config, status=403)
        # add index files
        if self.url == '/':
            self.url = os.path.join(self.config.document_root, self.INDEX_FILE)
        else:
            self.url = self.url.lstrip('/')
            self.url = os.path.join(self.config.document_root, self.url)

        # check that it is dir
        if os.path.isdir(self.url):
            self.url = os.path.join(self.url, self.INDEX_FILE)
            if not os.path.exists(self.url):
                return Response(self.config, status=403)
        # check that thi is file
        if not os.path.isfile(self.url):
            return Response(self.config, status=404)

        return None
