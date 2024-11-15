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


def parse_filenames(message):
    """Parses a Kafka message into a file names for s3 upload.

    Args:
        message (Message): Any Kafka message

    Returns:
        fileName (string): The Key for S3's put_object method, formatted as `topics/<topic>/<encodedPartition>/<topic>+<kafkaPartition>+<startOffset>.<format>` defined at https://docs.confluent.io/kafka-connectors/s3-sink/current/overview.html#s3-object-names
        messageKeyFileName (string): The Key for S3's put_object method, formatted as `topics/<topic>/<encodedPartition>/<topic>+<kafkaPartition>+<startOffset>.<format>` defined at https://docs.confluent.io/kafka-connectors/s3-sink/current/overview.html#s3-object-names
        headersFileName (string): The Key for S3's put_object method, formatted as `topics/<topic>/<encodedPartition>/<topic>+<kafkaPartition>+<startOffset>.<format>` defined at https://docs.confluent.io/kafka-connectors/s3-sink/current/overview.html#s3-object-names

    """
    # Kafka limits topic characters to ASCII alphanumerics, '.', '_' and '-'
    topic = message.topic()
    offset = message.offset()
    partition = message.partition()
    file_name = f"topics/{topic}/partition={partition}/{topic}+{partition}+{offset}.bin"
    message_key_file_name = f"{file_name}.keys.bin" if message.key() else None
    headers_file_name = f"{file_name}.headers.bin" if message.headers() else None

    return file_name, message_key_file_name, headers_file_name


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
            file_name, message_key_file_name, headers_file_name = parse_filenames(
                message
            )
            s3_client.put_object(
                Bucket=bucketName,
                Key=file_name,
                Body=message.value(),
            )

            if message_key_file_name is not None:
                s3_client.put_object(
                    Bucket=bucketName,
                    Key=message_key_file_name,
                    Body=message.key(),
                )

            if headers_file_name is not None:
                s3_client.put_object(
                    Bucket=bucketName,
                    Key=headers_file_name,
                    Body=json.dumps(
                        dict(message.headers()), indent=2, default=lambda x: x.decode()
                    ).encode(),
                )

            if error := message.error():
                log.error("topic %s: got error %s", topic, error)
            else:
                log.info("topic %s: got message", topic)
                partition = message.partition()
                metrics.received.labels(topic, partition).inc()
