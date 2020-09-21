import asyncio
import os
import socket
from multiprocessing import Process
from src.config import Config
from src.worker import Worker

class Server:
    def __init__(self, config: Config):
        self.config = config

    def run(self):
        self._create_socket()
        print(f'server started on  {self.config.host}:{self.config.port}')

        workers = []
        for x in range(self.config.cpu_limit):
            w = Worker(self._sock, self.config)
            workers.append(w)
            w.start()
        try:
            for w in workers:
                w.join()
        except KeyboardInterrupt:
            for w in workers:
                w.terminate()
        finally:
            self._sock.close()

    def _create_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.config.host, self.config.port))
        sock.listen(self.config.queue_size)

        self._sock = sock
