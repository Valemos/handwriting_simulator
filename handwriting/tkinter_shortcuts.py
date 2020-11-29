

def str_is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def update_integer_field(field):
    if not str_is_int(field.get()):
        field.set(str(int('0' + ''.join((i for i in field.get() if i.isdigit())))))


def get_index_name(name, index):
    return f"{index}.{name}" if name != '' else f"{index}"
