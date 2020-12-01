
class LengthObjectSerializer:

    @staticmethod
    def write_length_object(stream, object_bytes, lenght_bytes=2):
        stream.write(len(object_bytes).to_bytes(lenght_bytes, "big"))
        stream.write(object_bytes)

    @staticmethod
    def read_length_object(stream, lenght_bytes=2):
        obj_len = int.from_bytes(stream.read(lenght_bytes), 'big')
        return stream.read(obj_len)