#!/usr/bin/env python
from datetime import datetime
import os

from kombu import Exchange, Queue
import mongoengine

from application.models import User


exchange = Exchange(
    os.environ.get('EVENTS_EXCHANGE_NAME', 'events'),
    type='topic')
queue = Queue(
    os.environ.get('EVENTS_QUEUE_NAME', 'userstore-prototype'),
    exchange)
mongoengine.connect(host=os.environ.get('MONGO_URI'))


def is_login_message(body):
    return (
        isinstance(body, dict) and
        body.get('entity') == 'USER' and
        body.get('action') == 'LOGIN')


def parse_message(body):
    uid = body['user_id'].strip()
    timestamp = datetime.fromtimestamp(float(body['timestamp']))

    return uid, timestamp


def record_login(uid, timestamp):

    try:
        user = User.objects.get(user_id=uid)

    except User.DoesNotExist:
        user = User.objects.create(user_id=uid, created=timestamp)

    user.update(last_login=timestamp)


def process_message(body, message):

    if is_login_message(body):
        record_login(*parse_message(body))
        message.ack()


if __name__ == '__main__':
    from kombu import Connection

    conn = Connection(os.environ.get('BROKER_URI'))

    with conn.Consumer(queue, callbacks=[process_message]) as consumer:

        try:
            while True:
                conn.drain_events()

        except KeyboardInterrupt:
            pass
