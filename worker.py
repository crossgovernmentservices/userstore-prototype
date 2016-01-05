#!/usr/bin/env python
import os
import json
from datetime import datetime

from kombu.mixins import ConsumerMixin
from kombu.log import get_logger
from kombu import Exchange, Queue

from mongoengine import connect

from application.models import User

import boto3

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
            user_id = body['user_id'].strip()

            # mongoengine fails to parse timestamp fields, so manually coerce
            timestamp = datetime.fromtimestamp(float(body['timestamp']))

            logger.info('Processing user: %s', user_id)
            try:
                user = User.objects.get(user_id=user_id)
                action = 'Updated'
            except User.DoesNotExist:
                user = User(user_id=user_id, created=timestamp)
                action = 'Created'

            user.last_login = timestamp
            user.save()

            logger.info('%s user %s', action, user_id)
            message.ack()


class SNSSQSWorker(object):

    def __init__(self):
        # create SNS topic
        self.sns = boto3.resource('sns')
        self.topic = self.sns.create_topic(Name='Events')

        # create SQS queue
        self.sqs = boto3.resource('sqs')
        self.queue = self.sqs.create_queue(QueueName='EventQueue')

        # add policy to allow queue to receive messages from topic
        self.queue.set_attributes(Attributes={
            'Policy': json.dumps({
                "Version": "2012-10-17",
                "Id": "SNS-SQS-EventQueue-Policy",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "*",
                    },
                    "Action": "SQS:SendMessage",
                    "Resource": self.queue.attributes['QueueArn'],
                    "Condition": {
                        "ArnEquals": {
                            "aws:SourceArn": self.topic.attributes['TopicArn']
                        }
                    }
                }]
            })
        })

        # subscribe queue to topic
        self.topic.subscribe(
            Protocol='sqs',
            Endpoint=self.queue.attributes['QueueArn']
        )

    def run(self):
        while True:
            messages = self.queue.receive_messages(
                WaitTimeSeconds=10,
                MessageAttributeNames=['.*'])

            for message in messages:
                # lol?
                body = json.loads(json.loads(message.body)['Message'])
                logger.info('Processing message with body %s', body)
                self.process_message(body, message)

    def process_message(self, body, message):
        logger.info('Got message: body=%s, message=%s', body, message)

        if body['entity'] == 'USER' and body['action'] == 'LOGIN':
            user_id = body['user_id'].strip()

            # mongoengine fails to parse timestamp fields, so manually coerce
            timestamp = datetime.fromtimestamp(float(body['timestamp']))

            logger.info('Processing user: %s', user_id)
            try:
                user = User.objects.get(user_id=user_id)
                action = 'Updated'
            except User.DoesNotExist:
                user = User(user_id=user_id, created=timestamp)
                action = 'Created'

            user.last_login = timestamp
            user.save()

            logger.info('%s user %s', action, user_id)
            message.delete()


if __name__ == '__main__':
    from kombu import Connection
    from kombu.utils.debug import setup_logging
    # setup root logger
    setup_logging(loglevel='INFO', loggers=[''])

    try:
        worker = SNSSQSWorker()
        worker.run()
    except KeyboardInterrupt:
        exit(0)

    # with Connection(os.environ.get('BROKER_URI')) as conn:
    #     try:
    #         worker = Worker(conn)
    #         worker.run()
    #     except KeyboardInterrupt:
    #         print('bye bye')
