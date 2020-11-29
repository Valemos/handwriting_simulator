
class GridManager:

    @staticmethod
    def put_objects_on_grid(grid_rows, arguments=None):
        """
        To correctly put objects in one grid, they must have the same parent element
        That can be packed as grid
        :param grid_rows: rows with objects to place inside their parent
        :param arguments: additional global aguments that will be applied to every grid entry
        """
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

