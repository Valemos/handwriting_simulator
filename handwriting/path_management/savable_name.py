from abc import ABC

from handwriting.length_object_serializer import LengthObjectSerializer


class SavableName(ABC, LengthObjectSerializer):
    @staticmethod
    def read_name(stream):
        """
        Must be implemented with write_name()
        This handler must be overridden in classes, that have name, which needs to be serialized
        Must use stream_read_str to deserialize name attribute of an object
        :param stream: stream where to read
        :return: string object with name,
                None if name must not be read from stream
        """
        raise NotImplementedError

    def write_name(self, stream):
        """
        Must be implemented with read_name()
        Must use stream_write_str to serialize name attribute of an object
        :param stream: stream where to write
        :return:
        """
        raise NotImplementedError


    @staticmethod
    def stream_write_str(stream, name):
        """
        Writes name length and name itself to byte stream
        :param name: name string with no more than 128 characters
        :param stream: output byte stream
        """
        name_bytes = name[:128].encode('utf-8')
        LengthObjectSerializer.write_length_object(stream, name_bytes, 1)

    @staticmethod
    def stream_read_str(stream):
        """
        Function assumes, that first byte is a length N of a utf-8 string
        than it reads N bytes, decodes it and returns resulting stream
        :param stream: input byte stream
        :return: string object on top of stream
        """
        return LengthObjectSerializer.read_length_object(stream, 1).decode('utf-8')

