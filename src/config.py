DEFAULT_CPU_LIMIT = 4
DEFAULT_HOST = '0.0.0.0'
DEFAULT_PORT = 8080
DEFAULT_DOCUMENT_ROOT = '/var/www/html'
DEFAULT_QUEUE_SIZE = 32
DEFAULT_TIMEOUT = 15
DEFAULT_RECEIVE_BUFFSIZE = 1024
DEFAULT_FILE = 'index.html'


class Config:
    def __init__(self):
        self.cpu_limit = DEFAULT_CPU_LIMIT
        self.host = DEFAULT_HOST
        self.port = DEFAULT_PORT
        self.document_root = DEFAULT_DOCUMENT_ROOT
        self.queue_size = DEFAULT_QUEUE_SIZE
        self.timeout = DEFAULT_TIMEOUT
        self.buff_size = DEFAULT_RECEIVE_BUFFSIZE
