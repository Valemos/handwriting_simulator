from handwriting.stream_savable import StreamSavable


class StreamSavableCollection(StreamSavable):

    # this is reference to a class, which also is StreamSavableCollection
    child_class: StreamSavable = None

    def __init__(self, list_object=None):
        super().__init__()
        if self.child_class is None or list_object is None:
            raise NotImplementedError

        self.components = list_object

    def __eq__(self, other):
        return all(map(lambda x, y: x == y, self.components, other.components))

    @classmethod
    def read_next(cls, byte_stream):
        """
        function reads name of object
        Than reads multiple objects from the same byte stream

        If N is zero, than it indicates, that object has no name, but still contains HandwrittenPath objects

        If N is not zero, reads the name, than reads first object

        :param byte_stream: stream to read from
        :return: New instance of an object of this class,
                or None, if this object was empty
        """

        cls.stream_read_str(byte_stream)
        new_group = cls('')

        # check if first Curve object is not empty
        first_path = cls.child_class.read_next(byte_stream)
        if first_path is not None:
            paths = [first_path]
            while True:
                read_component = cls.child_class.read_next(byte_stream)
                if read_component is not None:
                    paths.append(read_component)
                else:
                    break
            new_group.paths = paths

        return new_group if not new_group.empty() else None

    def write_to_stream(self, byte_stream):
        """
        Writes object binary representation to byte stream

        If name is empty, but components list is not,
        1 zero byte will be written to indicate that name is empty, and continue writing Curve objects

        If name is not empty, but path does not contain any Curves,
        writs name as usual, and instead of no bytes at all for Curves list,
        writs zero length for Curves objects list

        To detect, that previous upper level object list is finished,
        write one empty child_object representation to file
        normally, this is 1 zero byte for name and 4 zero bytes for one empty child object

        :param byte_stream: stream where to write
        """

        if "name" in self.__dict__:
            self.stream_write_str(getattr(self, "name"), byte_stream)

        for component in self.components:
            component.write_to_stream(byte_stream)

        # empty object
        self.child_class.empty_instance().write_to_stream(byte_stream)

    @staticmethod
    def stream_write_str(name, stream):
        """
        Writes name length and name itself to byte stream
        :param name: name string with no more than 128 characters
        :param stream: output byte stream
        """
        name_bytes = name[:128].encode('utf-8')
        name_size = (len(name_bytes)).to_bytes(1, 'big')
        stream.write(name_size)
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

    def empty(self):
        """
        To read objects from files correctly, we assume that empty object is the object
        which have name '' and at the same time components list is empty

        if name is not empty, this path could have no objects in it.
        but, at the same time, have a name

        if name is empty, but objects is not, it is also a valid object,
        because we do not necessarly need a name to access this path from PathGroup
        """
        return len(self.components) == 0
