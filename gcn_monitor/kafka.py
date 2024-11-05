#
# Copyright © 2023 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
"""Monitor Kafka consumer connectivity."""

import json
import logging

import boto3
import gcn_kafka

from . import metrics

log = logging.getLogger(__name__)
s3_client = boto3.client("s3")


def stats_cb(data):
    stats = json.loads(data)
    for broker in stats["brokers"].values():
        metrics.broker_state.labels(broker["name"]).state(broker["state"])


def format_object(o):
    if type(o) is bytes:
        try:
            return o.decode()
        except UnicodeDecodeError as e:
            print(e)
            return o.decode("latin-1")
    else:
        return str(o)


def get_json(obj):
    return json.loads(
        json.dumps(obj, default=lambda o: getattr(o, "__dict__", format_object(o)))
    )


def parse_into_s3_object(message):
    """Parses a Kafka message into a key and body.

    Args:
        message (Message): Any Kafka message

    Returns:
        key (string): The Key for S3's put_object method, formatted as `topics/<topic>/<encodedPartition>/<topic>+<kafkaPartition>+<startOffset>.<format>` defined at https://docs.confluent.io/kafka-connectors/s3-sink/current/overview.html#s3-object-names

        body (dict): The Kafka message converted to a dict to be JSON serializable to include all fields available, such as:
        - error
        - headers
        - key
        - latency
        - leader_epoch
        - offset
        - partition
        - timestamp
        - topic
        - value

    """
    # Kafka limits topic characters to ASCII alphanumerics, '.', '_' and '-'
    topic = message.topic()
    offset = message.offset()
    partition = message.partition()
    key = f"topics/{topic}/partition={partition}/{topic}+{partition}+{offset}.json"
    properties = [
        method_name
        for method_name in dir(message)
        if not method_name.startswith("__") and not method_name.startswith("set_")
    ]

    value = {}
    for messageKey in properties:
        attr_value = getattr(message, messageKey)
        if isinstance(attr_value(), bytes) and callable(attr_value):
            value[messageKey] = attr_value().decode()
        elif callable(attr_value):
            value[messageKey] = attr_value()
        elif isinstance(attr_value, bytes):
            value[messageKey] = attr_value.decode()
        else:
            value[messageKey] = attr_value

    return key, get_json(value)


def run(bucketName):
    log.info("Creating consumer")
    config = gcn_kafka.config_from_env()
    config["stats_cb"] = stats_cb
    config["statistics.interval.ms"] = 1e3
    consumer = gcn_kafka.Consumer(config)

    log.info("Subscribing")
    topics = list(consumer.list_topics().topics.keys())
    consumer.subscribe(topics)

    log.info("Entering consume loop")
    while True:
        for message in consumer.consume(timeout=1):
            topic = message.topic()
            key, body = parse_into_s3_object(message)
            s3_client.put_object(
                Bucket=bucketName,
                Key=key,
                Body=body,
            )
            if error := message.error():
                log.error("topic %s: got error %s", topic, error)
            else:
                log.info("topic %s: got message", topic)
                partition = message.partition()
                metrics.received.labels(topic, partition).inc()
