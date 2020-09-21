DEFAULT_CONFIG = '/etc/httpd.conf'

from src.server import Server
from src.config import Config

if __name__ == '__main__':
    config = Config()
    server = Server(config)
    server.run()
