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
    #sid = yield from nc.subscribe("foo", cb=message_handler)

    # Stop receiving after 2 messages.
    #yield from nc.auto_unsubscribe(sid, 2)
    while True:
        yield from nc.publish("foo", b'Hello')
        print('sent')
        yield from asyncio.sleep(10, loop=loop)

    @asyncio.coroutine
    def help_request(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print("Received a message on '{subject} {reply}': {data}".format(
          subject=subject, reply=reply, data=data))
        yield from nc.publish(reply, b'I can help')

    # Use queue named 'workers' for distributing requests
    # among subscribers.
    #yield from nc.subscribe("help", "workers", help_request)

    # Send a request and expect a single response
    # and trigger timeout if not faster than 50 ms.
    try:
        response = yield from nc.timed_request("help", b'help me', 0.050)
        print("Received response: {message}".format(message=response.data.decode()))
    except ErrTimeout:
        print("Request timed out")

    yield from asyncio.sleep(1, loop=loop)
    yield from nc.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()