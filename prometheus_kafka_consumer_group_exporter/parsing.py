from struct import unpack_from, error as struct_error
import logging

def read_short(bytes):
    num = unpack_from('>h', bytes)[0]
    remaining = bytes[2:]
    return (num, remaining)


def read_int(bytes):
    num = unpack_from('>i', bytes)[0]
    remaining = bytes[4:]
    return (num, remaining)


def read_long_long(bytes):
    num = unpack_from('>q', bytes)[0]
    remaining = bytes[8:]
    return (num, remaining)


def read_string(bytes):
    length, remaining = read_short(bytes)
    string = remaining[:length].decode('utf-8')
    remaining = remaining[length:]
    return (string, remaining)


def parse_key(bytes):
    try:
        (version, remaining_key) = read_short(bytes)
        if version == 1 or version == 0:
            # https://github.com/apache/kafka/blob/2.1.1/core/src/main/scala/kafka/coordinator/group/GroupMetadataManager.scala#L936-L938
            (group, remaining_key) = read_string(remaining_key)
            (topic, remaining_key) = read_string(remaining_key)
            (partition, remaining_key) = read_int(remaining_key)
            return (version, group, topic, partition)
    except struct_error:
        logging.warn("Failed to parse key")


def parse_value(bytes):
    try:
        (version, remaining_key) = read_short(bytes)
        if version == 0:
            # https://github.com/apache/kafka/blob/2.1.1/core/src/main/scala/kafka/coordinator/group/GroupMetadataManager.scala#L943-L945
            (offset, remaining_key) = read_long_long(remaining_key)
            (metadata, remaining_key) = read_string(remaining_key)
            (timestamp, remaining_key) = read_long_long(remaining_key)
            return (version, offset, metadata, timestamp)
        elif version == 1:
            # https://github.com/apache/kafka/blob/2.1.1/core/src/main/scala/kafka/coordinator/group/GroupMetadataManager.scala#L950-L953
            (offset, remaining_key) = read_long_long(remaining_key)
            (metadata, remaining_key) = read_string(remaining_key)
            (commit_timestamp, remaining_key) = read_long_long(remaining_key)
            (expire_timestamp, remaining_key) = read_long_long(remaining_key)
            return (version, offset, metadata, commit_timestamp, expire_timestamp)
        elif version == 2:
            # https://github.com/apache/kafka/blob/2.1.1/core/src/main/scala/kafka/coordinator/group/GroupMetadataManager.scala#L959-L961
            (offset, remaining_key) = read_long_long(remaining_key)
            (metadata, remaining_key) = read_string(remaining_key)
            (commit_timestamp, remaining_key) = read_long_long(remaining_key)
            return (version, offset, metadata, commit_timestamp)
        elif version == 3:
            # https://github.com/apache/kafka/blob/2.1.1/core/src/main/scala/kafka/coordinator/group/GroupMetadataManager.scala#L966-L970
            (offset, remaining_key) = read_long_long(remaining_key)
            (leader_epoch, remaining_key) = read_int(remaining_key)
            (metadata, remaining_key) = read_string(remaining_key)
            (commit_timestamp, remaining_key) = read_long_long(remaining_key)
            return (version, offset, metadata, commit_timestamp)
        else:
            logging.warn("Did not recognize value schema version")
    except struct_error:
        logging.warn("Failed to parse value")
