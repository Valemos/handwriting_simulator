import io
import pickle
from pickletools import optimize

from abc import ABC, abstractmethod

from handwriting.misc.exceptions import LoadingException, SavingException
from handwriting.misc.stream_serialization import *


class IStreamSavable(ABC):

    def write_to_stream(self, byte_stream):
        try:
            bytes_ = pickle.dumps(self)
            assert len(bytes_) <= 2147483647

            write_length_object(byte_stream, optimize(bytes_), 4)

        except (pickle.PickleError, AssertionError):
            SavingException("error saving curve to bytes!")

    @staticmethod
    def read_next(byte_stream):
        """throws LoadingException if cannot load anymore"""
        try:
            bytes_ = read_length_object(byte_stream, 4)
            return pickle.loads(bytes_)

        except (pickle.PickleError, EOFError):
            raise LoadingException("error loading curve from bytes")

    def get_bytes(self):
        """
        :return: binary representation of this object
        """
        bin_stream = io.BytesIO()
        self.write_to_stream(bin_stream)
        return bin_stream.getvalue()

    @staticmethod
    @abstractmethod
    def empty_instance():
        pass
