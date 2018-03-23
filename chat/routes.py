import pathlib

from .views import chat_room, create_channel, delete_channel, index, websocket

PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/{channel}', chat_room)
    app.router.add_get('/ws/{channel}', websocket)
    app.router.add_get('/create_channel/{channel}', create_channel)
    app.router.add_post('/delete_channel/{channel}', delete_channel)


def setup_static_routes(app):
    app.router.add_static(
        '/static/', path=PROJECT_ROOT / 'static', name='static')
