import json
import logging

import aiohttp_jinja2
import petname
from aiohttp import WSMsgType, web

from chat.broadcast import EventsChannel

log = logging.getLogger(__name__)


async def index(request):
    channels = await EventsChannel.get_channels(request.app)
    return aiohttp_jinja2.render_template(
        'index.html', request, {'channels': channels})


async def create_channel(request):
    channel_name = request.match_info['channel']
    if channel_name == 'random':
        channel_name = 'channel:' + petname.Generate()
    channel = EventsChannel(request.app, channel_name)
    await channel.create()
    return web.HTTPFound('/')


async def delete_channel(request):
    channel = EventsChannel(request.app, request.match_info['channel'])
    await channel.delete()
    return web.HTTPFound('/')


async def chat_room(request):
    channel_name = request.match_info['channel']
    if not EventsChannel(request.app, channel_name).exists():
        return web.HTTPNotFound()
    return aiohttp_jinja2.render_template(
        'chat.html', request, {'channel': channel_name})


async def websocket(request):
    resp = web.WebSocketResponse()
    await resp.prepare(request)
    name = petname.Name().capitalize()
    log.info('%s joined.', name)
    channel_name = request.match_info['channel']
    channel = EventsChannel(request.app, channel_name)
    if not channel.exists():
        log.warning(f'No such channel [{channel_name}]')
        await resp.close()
        return resp
    try:
        channel.subscribe_socket(resp, name)
        await channel.publish(json.dumps(
            {'action': 'join', 'name': name}))
        async for msg in resp:
            if msg.type != WSMsgType.text:
                break
            await channel.publish(json.dumps(
                {'action': 'sent', 'name': name, 'text': msg.data}))
    finally:
        channel.unsubscribe_socket(name)
        await channel.publish(json.dumps(
            {'action': 'disconnect', 'name': name}))
        log.info('%s disconnected.', name)

    return resp
