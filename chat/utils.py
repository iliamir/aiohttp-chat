import json

import aioredis

import settings


async def setup_redis(app):
    app['redis'] = await aioredis.create_redis(settings.REDIS_HOST)


def format_message(raw_msg):
    try:
        json.loads(raw_msg)
    except json.JSONDecodeError:
        return json.dumps(
            {'action': 'sent', 'name': '@big_aye@', 'text': raw_msg})
    return raw_msg
