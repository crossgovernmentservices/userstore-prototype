#!/usr/bin/env python
import os
from datetime import datetime

from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu import Exchange, Queue

from mongoengine import connect

from application.models import User

logger = get_logger(__name__)

exchange = Exchange('events', type='topic')
queue = Queue('userstore-prototype', exchange)


class Worker(ConsumerMixin):
    def __init__(self, connection):
        self.connection = connection
        connect(host=os.environ.get('MONGO_URI'))

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=[queue],
                         accept=['json'],
                         callbacks=[self.process_message])]

    def process_message(self, body, message):
        logger.info('Got message: body=%s, message=%s', body, message)

        if body['entity'] == 'USER' and body['action'] == 'LOGIN':
            email = body['context']['email'].strip()

            # mongoengine fails to parse timestamp fields, so manually coerce
            timestamp = datetime.fromtimestamp(float(body['timestamp']))

            logger.info('Processing user: %s', email)
            try:
                user = User.objects.get(email=email)
                action = 'Updated'
            except User.DoesNotExist:
                user = User(email=email, created=timestamp)
                action = 'Created'

            user.last_login = timestamp
            user.save()

            logger.info('%s user %s', action, email)
            message.ack()


if __name__ == '__main__':
    from kombu import Connection
    from kombu.utils.debug import setup_logging
    # setup root logger
    setup_logging(loglevel='INFO', loggers=[''])

    with Connection(os.environ.get('BROKER_URI')) as conn:
        try:
            worker = Worker(conn)
            worker.run()
        except KeyboardInterrupt:
            print('bye bye')
