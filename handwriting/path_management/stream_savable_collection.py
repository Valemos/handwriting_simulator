from abc import ABC

from handwriting.path_management.savable_name import SavableName
from handwriting.path_management.stream_savable import StreamSavable


class StreamSavableCollection(StreamSavable, SavableName, ABC):

    # this is reference to a class, which also is StreamSavableCollection
    child_class: StreamSavable = None

    def __init__(self, list_object):
        if self.child_class is None:
            raise NotImplementedError

        self.components = list_object

    def __eq__(self, other):
        return all(map(lambda x, y: x == y, self.components, other.components))

    @classmethod
    def read_next(cls, byte_stream):
        """
        handler reads name of object
        Than reads multiple canvas_objects from the same byte stream

        If N is zero, than it indicates, that object has no name, but still contains HandwrittenPath canvas_objects

        If N is not zero, reads the name, than reads first object

        :param byte_stream: stream to read from
        :return: New instance of an object of this class,
                or None, if this object was empty
        """

        name = cls.read_name(byte_stream)
        if name is None:
            new_obj = cls()
        else:
            new_obj = cls(name)

        # check if first Curve object is not empty
        first_path = cls.child_class.read_next(byte_stream)
        if first_path is not None:
            components = [first_path]
            while True:
                read_component = cls.child_class.read_next(byte_stream)
                if read_component is not None:
                    components.append(read_component)
                else:
                    break
            new_obj.components = components

        return new_obj if not new_obj.empty() else None

    def write_to_stream(self, byte_stream):
        """
        Writes object binary representation to byte stream

        If name is empty, but components list is not,
        1 zero byte will be written to indicate that name is empty, and continue writing Curve canvas_objects

        If name is not empty, but path does not contain any Curves,
        writs name as usual, and instead of no bytes at all for Curves list,
        writs zero length for Curves canvas_objects list

        To detect, that previous upper level object list is finished,
        write one empty child_object representation to file
        normally, this is 1 zero byte for name and 4 zero bytes for one empty child object

        :param byte_stream: stream where to write
        """

        self.write_name(byte_stream)
        for component in self.components:
            component.write_to_stream(byte_stream)

        # empty object
        self.child_class.empty_instance().write_to_stream(byte_stream)

    def empty(self):
        """
        To read canvas_objects from files correctly, we assume that empty object is the object
        which have name '' and at the same time components list is empty

        if name is not empty, this path could have no canvas_objects in it.
        but, at the same time, have a name

        if name is empty, but canvas_objects is not, it is also a valid object,
        because we do not necessarly need a name to access this path from PathGroup
        """
        return len(self.components) == 0
