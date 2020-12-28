import io
import pickle
from abc import ABC

from handwriting.length_object_serializer import LengthObjectSerializer


class IStreamSavable(LengthObjectSerializer, ABC):

    def write_to_stream(self, byte_stream):
        try:
            b = pickle.dumps(self)
            assert len(b) <= 2147483647

            self.write_length_object(byte_stream, b, 4)

        except (pickle.PicklingError, AssertionError):
            print("error saving curve to bytes!")

    @classmethod
    def read_next(cls, byte_stream):
        try:
            bytes_ = cls.read_length_object(byte_stream, 4)
            if len(bytes_) > 0:
                return pickle.loads(bytes_)
            else:
                return None

        except pickle.UnpicklingError:
            print("error loading curve from bytes")
            return None

    def get_bytes(self):
        """
        :return: binary representation of this object
        """
        bin_stream = io.BytesIO()
        self.write_to_stream(bin_stream)
        return bin_stream.getvalue()
