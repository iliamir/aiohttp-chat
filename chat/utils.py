import datetime
import json

import aioredis
import motor.motor_asyncio
import pymongo.errors

import settings


class Storage:

    max_messages = 10

    def __init__(self, host):
        self._storage = motor.motor_asyncio.AsyncIOMotorClient(host)

    async def get_channels(self):
        cursor = self._storage['chat']['rooms'].find()
        return [item['_id'] for item in await cursor.to_list(length=1000)]

    async def get_channel(self, channel):
        return await self._storage['chat']['rooms'].find_one(
            {'_id': channel},
        )

    async def create_channel(self, channel):
        try:
            await self._storage['chat']['rooms'].insert_one(
                {'_id': channel, 'members': []},
            )
        except pymongo.errors.DuplicateKeyError:
            pass

    async def delete_channel(self, channel):
        await self._storage['chat']['rooms'].remove(
            {'_id': channel},
        )

    async def get_messages(self, channel):
        cursor = self._storage['chat']['messages'].find(
            {'channel': channel, 'msg.action': 'sent'},
            {'_id': 0, 'date': 0},
        ).sort('date')
        return await cursor.to_list(length=self.max_messages)

    async def purge_messages(self, channel):
        self._storage['chat']['messages'].remove({
            'channel': channel,
        })

    async def save_message(self, channel, msg):
        await self._storage['chat']['messages'].insert_one(
            {
                'channel': channel,
                'msg': json.loads(msg),
                'date': datetime.datetime.utcnow(),
            },
        )


def setup_storage(app):
    app['storage'] = Storage(settings.MONGO_HOST)


def setup_redis(app):
    app['redis'] = aioredis.create_redis(settings.REDIS_HOST)


def setup_mongo(app):
    app['mongo'] = motor.motor_asyncio.AsyncIOMotorClient()


def format_message(raw_msg):
    try:
        json.loads(raw_msg)
    except json.JSONDecodeError:
        return json.dumps(
            {'action': 'sent', 'name': '$_GodUser', 'text': raw_msg})
    return raw_msg
