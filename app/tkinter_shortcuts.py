from handwriting.signature_dictionary import SignatureDictionary


def bind_handlers(handler, first_part=None, second_part=None):
    """
    Recursively takes dictionary of dictionaries of tuples
    and combines them to bind tkinter event functions to objects

    :param handler: object to iterate through
    :param first_part: the first part of command
    :param second_part: the second part of command
    :return:
    """
    if isinstance(handler, dict):
        for part, func in handler.items():
            if first_part is None:
                bind_handlers(func, part)
            else:
                bind_handlers(func, first_part, part)
        return

    if isinstance(handler, list):
        for func in handler:
            bind_handlers(func, first_part, second_part)
        return

    if isinstance(handler, tuple):
        bind_object, handler = handler
        bind_object.bind(f"<{first_part}>"
                         if second_part is None else
                         f"<{first_part}-{second_part}>",
                         handler)
    else:
        raise ValueError("handler is not a tuple of object and function")


def put_objects_on_grid(grid_rows, arguments=None):
    for row in range(len(grid_rows)):
        for col in range(len(grid_rows[row])):
            if grid_rows[row][col] is None:
                continue
            elif isinstance(grid_rows[row][col], tuple):
                obj, args = grid_rows[row][col]
                if arguments is not None:
                    for arg_name, value in arguments.items():
                        if arg_name not in args:
                            args[arg_name] = value

                obj.grid(row=row, column=col, **args)
            else:
                grid_rows[row][col].grid(row=row, column=col, **arguments)


def str_is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def update_integer_field(field):
    if not str_is_int(field.get()):
        field.set(str(int('0' + ''.join((i for i in field.get() if i.isdigit())))))



def open_dictionary_file(file_path):
    """Initializes signature dictionary and dictionary irerator"""
    dct = SignatureDictionary.from_file(file_path)
    it = None
    if dct is not None:
        it = dct.get_iterator()
    return dct, it
