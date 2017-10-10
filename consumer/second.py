import asyncio
import time
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers


def run(loop):
    nc = NATS()
    yield from nc.connect(io_loop=loop)

    @asyncio.coroutine
    def message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print("Received a message on '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))

    # Simple publisher and async subscriber via coroutine.
    sid = yield from nc.subscribe("foo", "second", cb=message_handler)

    # Stop receiving after 2 messages.
    #yield from nc.auto_unsubscribe(sid, 2)
    #yield from nc.publish("foo", b'Hello')
    #yield from nc.publish("foo", b'World')
    #yield from nc.publish("foo", b'!!!!!')

    yield from asyncio.sleep(30, loop=loop)
    yield from nc.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()