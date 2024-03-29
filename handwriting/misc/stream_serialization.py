def write_length_object(stream, object_bytes, length_bytes=2):
    # ! can cause errors when length bytes cannot hold size of an object_bytes
    stream.write(len(object_bytes).to_bytes(length_bytes, "big"))
    stream.write(object_bytes)


def read_length_object(stream, length_bytes=2):
    obj_len = int.from_bytes(stream.read(length_bytes), 'big')
    return stream.read(obj_len)
