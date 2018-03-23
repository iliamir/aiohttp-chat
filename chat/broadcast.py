import logging

import aioredis

import settings
from chat.utils import format_message

logger = logging.getLogger(__name__)


class EventsChannel:

    def __init__(self, app, name):
        self.app = app
        self.channel_name = name
        self._publisher = None

    async def create(self):
        if not self.exists():
            await self.app['redis'].sadd('rooms', self.channel_name)
            self.broadcast()

    async def delete(self):
        self.app['events_channels'].pop(self.channel_name).cancel()
        await self.app['redis'].srem('rooms', self.channel_name)
        for ws in self.app['sockets'].pop(self.channel_name, {}).values():
            await ws.close()

    @staticmethod
    async def get_channels(app):
        return await app['redis'].smembers('rooms', encoding='utf-8')

    @classmethod
    async def propagate_channels(cls, app):
        for channel_name in await cls.get_channels(app):
            await cls(app, channel_name).create()

    @classmethod
    async def cleanup_channels(cls, app):
        for task in app['events_channels'].values():
            task.cancel()
            await task
        app['events_channels'].clear()

    def exists(self):
        return self.channel_name in self.app['events_channels']

    def subscribe_socket(self, ws, name):
        logging.debug(f'Subscriber of {self.channel_name} here!')
        self.app['sockets'][self.channel_name][name] = ws

    def unsubscribe_socket(self, name):
        logging.debug(f'Subscriber of {self.channel_name} has went!')
        self.app['sockets'][self.channel_name].pop(name, None)

    async def publish(self, msg):
        if self._publisher is None:
            self._publisher = await aioredis.create_redis(settings.REDIS_HOST)
        await self._publisher.publish(self.channel_name, msg)

    def broadcast(self):
        task = self.app.loop.create_task(self._broadcast())
        self.app['events_channels'][self.channel_name] = task

    async def _broadcast(self):
        logging.debug(f'Listener of {self.channel_name} here!')
        listener = await aioredis.create_redis(settings.REDIS_HOST)
        channel, *__ = await listener.subscribe(self.channel_name)
        while True:
            msg = await channel.get(encoding='utf-8')
            if msg is None:
                continue
            message = format_message(msg)
            for ws in self.app['sockets'][self.channel_name].values():
                await ws.send_str(message)
