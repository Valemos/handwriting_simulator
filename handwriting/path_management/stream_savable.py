import io
from abc import ABC


class StreamSavable(ABC):

    def write_to_stream(self, byte_stream):
        raise NotImplementedError

    @classmethod
    def read_next(cls, byte_stream):
        raise NotImplementedError

    def get_bytes(self):
        """
        :return: binary representation of this object
        """
        bin_stream = io.BytesIO()
        self.write_to_stream(bin_stream)
        return bin_stream.getvalue()

    @staticmethod
    def empty_instance():
        """
        :return: instance of this class, that is considered to be empty
        """
        raise NotImplementedError
