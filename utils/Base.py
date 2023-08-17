import json
from pprint import pprint


class Base:
    def __init__(self):
        pass

    def print(self, is_pretty: bool = False, exclude: list[str] = None):

        if is_pretty:
            print_obj = vars(self)
            if exclude:
                for ex in exclude:
                    print_obj.pop(ex, None)

            pprint(print_obj)
        else:
            print(vars(self))

    def write_to_disk(self, data, file_name):
        with open(file_name, 'w') as f:
            json.dump(data, f)
