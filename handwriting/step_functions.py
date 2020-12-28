
def step_backwards(num, mx):
    """
    Step in backward direction by 1 for some integer
    :param num: int number to step with
    :param mx: maximum value number can get to
    :return: number stepped back by 1
    """
    return (num - 1) if num > 0 else mx


def step_forwards(num, mx):
    """
    Step in forward direction by 1 for some integer
    :param num: int number to step with
    :param mx: next integer value after maximum number
    :return: number stepped forward by 1
    """
    return (num + 1) if num < mx else 0
