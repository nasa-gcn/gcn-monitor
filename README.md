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

2.  Install [pre-commit hooks](https://pre-commit.com) by running the following two commands:

        pip install pre-commit
        pre-commit install

3.  Install Poetry by following [their installation instructions](https://python-poetry.org/docs/#installation).

4.  Install this package and its dependencies by running the following command inside your clone of this repository:

        poetry install --all-extras

5.  Run the following command to launch a shell that is preconfigured with the project's virtual environment:

        poetry shell


## S3 Output

We are not currently using the S3 Sink connector. In its place, in `kafka.py` we are uploading files directly to an S3 bucket. The raw message value is uploaded as-is (a byte string). If a key is present on the message, it is also stored as a byte string. If headers are included in the message, their key-value pairs are parsed and stored as a JSON object, where the value is a base64 encoded string.

For example:

Headers provided in a message would be read in a python consumer from the `message.headers()` function as:
```
 [('header1', b'value'), ('header2', b'value2')]
```
and subsequently stored as:

```
{'header1': 'dmFsdWU=', 'header2': 'dmFsdWUy'}
```
