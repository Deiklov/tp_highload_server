import multiprocessing
import os
import asyncio
from pathlib import Path
import urllib.parse
from src.config import Config
from src.http_handler import Request, Response


class Worker(multiprocessing.Process):
    def __init__(self, sock, config: Config):
        super().__init__()
        self.loop = asyncio.get_event_loop()
        self.sock = sock
        self.config = config
        self._resp = Response(config)

    def run(self):
        try:
            self.loop.run_until_complete(self.work())
        except KeyboardInterrupt:
            print("Caught keyboard interrupt. Canceling tasks...")
        finally:
            print('Successfully shutdown worker.')
            self.loop.close()

    async def work(self):
        while True:
            conn, _ = await self.loop.sock_accept(self.sock)
            conn.settimeout(self.config.timeout)
            conn.setblocking(False)
            self.loop.create_task(self.handle_conn(conn))

    async def handle_conn(self, conn):
        req_data = await self.loop.sock_recv(conn, self.config.buff_size)

        req = Request(req_data.decode("utf-8"))
        response = await req.validate_request()
        if response is None:
            response = Response(self.config, method=req.method, status=200, path_to_file=req.url)
        await response.send(self.loop, conn)
        conn.close()
