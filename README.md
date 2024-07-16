# gcn-monitor

A Kafka client instrumented with Prometheus.

## Configuration

The following environment variables may be used to configure the service:

| Name                 | Value                                                                              |
| -------------------- | ---------------------------------------------------------------------------------- |
| `KAFKA_*`            | Kafka client configuration as understood by [Confluent Platform docker containers] |

[Confluent Platform docker containers]: https://docs.confluent.io/platform/current/installation/docker/config-reference.html

## How to contribute

This package uses [Poetry](https://python-poetry.org) for packaging and Python virtual environment management. To get started:

1.  [Fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) and [clone](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo#cloning-your-forked-repository) this repository.

2.  Install Poetry by following [their installation instructions](https://python-poetry.org/docs/#installation).

3.  Install this package and its dependencies by running the following command inside your clone of this repository:

        poetry install --all-extras

4.  Run the following command to launch a shell that is preconfigured with the project's virtual environment:

        poetry shell
