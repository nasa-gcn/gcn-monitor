from gcn_monitor.kafka import parse_filenames


class MockCimplMessage:
    def __init__(self, topic, offset, partition, key, headers):
        self._topic = topic
        self._offset = offset
        self._partition = partition
        self._key = key
        self._headers = headers

    def topic(self):
        return self._topic

    def offset(self):
        return self._offset

    def partition(self):
        return self._partition

    def key(self):
        return self._key

    def headers(self):
        return self._headers


def test_parse_filenames():
    mockMessage = MockCimplMessage(
        "example_topic",
        1,
        0,
        b"example key",
        [("header1", b"value"), ("header2", b"value2")],
    )

    file_name, message_key_file_name, headers_file_name = parse_filenames(mockMessage)

    assert file_name == "topics/example_topic/partition=0/example_topic+0+1.bin"
    assert (
        message_key_file_name
        == "topics/example_topic/partition=0/example_topic+0+1.bin.key.bin"
    )
    assert (
        headers_file_name
        == "topics/example_topic/partition=0/example_topic+0+1.bin.headers.json"
    )


def test_parse_filenames_without_key():
    mockMessage = MockCimplMessage(
        "example_topic",
        1,
        0,
        None,
        [("header1", b"value"), ("header2", b"value2")],
    )

    file_name, message_key_file_name, headers_file_name = parse_filenames(mockMessage)

    assert file_name == "topics/example_topic/partition=0/example_topic+0+1.bin"
    assert message_key_file_name is None
    assert (
        headers_file_name
        == "topics/example_topic/partition=0/example_topic+0+1.bin.headers.json"
    )


def test_parse_filenames_without_headers():
    mockMessage = MockCimplMessage(
        "example_topic",
        1,
        0,
        b"example key",
        None,
    )

    file_name, message_key_file_name, headers_file_name = parse_filenames(mockMessage)

    assert file_name == "topics/example_topic/partition=0/example_topic+0+1.bin"
    assert (
        message_key_file_name
        == "topics/example_topic/partition=0/example_topic+0+1.bin.key.bin"
    )
    assert headers_file_name is None
