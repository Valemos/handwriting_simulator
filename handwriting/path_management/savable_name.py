from abc import ABC


class SavableName(ABC):
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
    def stream_write_str(name, stream):
        """
        Writes name length and name itself to byte stream
        :param name: name string with no more than 128 characters
        :param stream: output byte stream
        """
        name_bytes = name[:128].encode('utf-8')
        stream.write(len(name_bytes).to_bytes(1, 'big'))
        stream.write(name_bytes)

    @staticmethod
    def stream_read_str(stream):
        """
        Function assumes, that first byte is a length N of a utf-8 string
        than it reads N bytes, decodes it and returns resulting stream
        :param stream: input byte stream
        :return: string object on top of stream
        """
        # if byte_stream does not contain any bytes, name_len equals to 0
        name_len = int.from_bytes(stream.read(1), 'big')

        # if name_len is zero, than empty string '' will be returned
        return (stream.read(name_len)).decode('utf-8')

