import asyncio
import logging
from collections import defaultdict

import aiohttp_jinja2
import jinja2
from aiohttp import web

from chat.broadcast import EventsChannel
from chat.routes import setup_routes, setup_static_routes
from chat.utils import setup_redis


async def init(loop):
    app = web.Application(loop=loop)
    app['sockets'] = defaultdict(dict)
    app['events_channels'] = {}
    app.on_shutdown.append(shutdown)
    app.on_cleanup.append(EventsChannel.cleanup_channels)
    aiohttp_jinja2.setup(
        app, loader=jinja2.PackageLoader('chat', 'templates'))
    setup_routes(app)
    setup_static_routes(app)
    await setup_redis(app)
    await EventsChannel.propagate_channels(app)
    return app


async def shutdown(app):
    for ch in app['sockets'].values():
        for ws in ch.values():
            await ws.close()
    app['sockets'].clear()


def main():
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init(loop))
    try:
        web.run_app(app, port=1488)
    except asyncio.CancelledError:
        pass


if __name__ == '__main__':
    main()
