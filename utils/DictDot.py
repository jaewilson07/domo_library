from types import SimpleNamespace


class DictDot(SimpleNamespace):
    def __init__(self, dictionary, **kwargs):
        super().__init__(**kwargs)

        for key, value in dictionary.items():
            if isinstance(value, dict):
                self.__setattr__(key, DictDot(value))
            elif isinstance(value, list):
                new_list = []
                for item in value:
                    if isinstance(item, dict):
                        new_list.append(DictDot(item))
                    else:
                        new_list.append(item)
                self.__setattr__(key, new_list)
            else:
                self.__setattr__(key, value)

    def __getattr__(self, item):
        return None
