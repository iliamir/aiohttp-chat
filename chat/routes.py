import pathlib

from .views import (LoginView, chat_room, create_channel, delete_channel,
                    get_last_messages, index, logout, websocket)

PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app):
    app.router.add_route('GET', '/', index)
    app.router.add_route('*', '/login', LoginView),
    app.router.add_route('GET', '/logout', logout)
    app.router.add_route('GET', '/last_messages/{channel}', get_last_messages)  # noqa
    app.router.add_route('GET', '/{channel}', chat_room)
    app.router.add_route('GET', '/ws/{channel}', websocket)
    app.router.add_route('GET', '/create_channel/{channel}', create_channel)  # noqa
    app.router.add_route('POST', '/delete_channel/{channel}', delete_channel)  # noqa


def setup_static_routes(app):
    app.router.add_static(
        '/static/', path=PROJECT_ROOT / 'static', name='static')
