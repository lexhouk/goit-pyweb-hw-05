from aiofile import async_open
from aiopath import AsyncPath
import asyncio
from datetime import datetime
import logging
from re import Match, search

import websockets
import names
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

from main import main as exchange

logging.basicConfig(level=logging.INFO)


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            command = search(r'^exchange\s*(\d*)$', message.strip())

            if isinstance(command, Match):
                path = AsyncPath('logs')

                if not await path.exists():
                    await path.mkdir()

                async with async_open(path / 'calls.log',
                                      'a',
                                      encoding='utf-8') as file:
                    await file.write(f'{datetime.now()}\t{ws.name}\t'
                                     f'{message}\n')

                days = int(command.group(1) or 1)
                message = ''

                for day_currencies in await exchange(days, []):
                    for date, currencies in day_currencies.items():
                        message += f'\n{date}:'

                        for currency, rates in currencies.items():
                            records = []

                            for key, value in rates.items():
                                if value is not None:
                                    records.append(f'{key}: {value} UAH')

                            if records:
                                message += '\n\t{}:\n\t\t{}'.format(
                                    currency,
                                    '\n\t\t'.join(records)
                                )

            await self.send_to_clients(f"{ws.name}: {message}")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
