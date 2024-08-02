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

import gcn_kafka

from . import metrics

log = logging.getLogger(__name__)


def stats_cb(data):
    stats = json.loads(data)
    for broker in stats["brokers"].values():
        metrics.broker_state.labels(broker["name"]).state(broker["state"])


def run():
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
            if error := message.error():
                log.error("topic %s: got error %s", topic, error)
            else:
                log.info("topic %s: got message", topic)
