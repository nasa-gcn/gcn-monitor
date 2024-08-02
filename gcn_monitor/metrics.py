#
# Copyright © 2023 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
"""Prometheus metrics."""

import prometheus_client

broker_state = prometheus_client.Enum(
    "state",
    "Kafka broker state (see https://github.com/confluentinc/librdkafka/blob/master/STATISTICS.md)",
    states=[
        # from https://github.com/confluentinc/librdkafka/blob/v2.2.0/src/rdkafka_broker.c#L83
        "INIT",
        "DOWN",
        "TRY_CONNECT",
        "CONNECT",
        "SSL_HANDSHAKE",
        "AUTH_LEGACY",
        "UP",
        "UPDATE",
        "APIVERSION_QUERY",
        "AUTH_HANDSHAKE",
        "AUTH_REQ",
    ],
    namespace="kafka",
    subsystem="broker",
    labelnames=["name"],
)

received = prometheus_client.Counter(
    "received",
    "Kafka records received",
    namespace="kafka",
    subsystem="records",
    labelnames=["topic", "partition"],
)
