def put_objects_on_grid(grid_rows, shared_args=None):
    """
    To correctly put canvas_objects in one grid, they must have the same parent element
    That can be packed as grid
    :param grid_rows: rows with canvas_objects to place inside their parent
    :param shared_args: additional global arguments that will be applied to every grid entry
    """

    for row in range(len(grid_rows)):
        for col in range(len(grid_rows[row])):
            if grid_rows[row][col] is None:
                continue
            elif isinstance(grid_rows[row][col], tuple):
                obj, args = grid_rows[row][col]
                if shared_args is not None:
                    for arg_name, value in shared_args.items():
                        if arg_name not in args:
                            args[arg_name] = value

                obj.grid(row=row, column=col, **args)
            else:
                grid_rows[row][col].grid(row=row, column=col, **shared_args)
