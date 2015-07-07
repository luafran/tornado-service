class DictAsObject(dict):  # pylint: disable=too-few-public-methods
    def __init__(self, *args, **kwargs):
        super(DictAsObject, self).__init__(*args, **kwargs)
        self.__dict__ = self


class DotNotationDict(dict):  # pylint: disable=too-few-public-methods
    def __init__(self, dictionary=None):
        self._dictionary = dictionary if dictionary is not None else {}
        super(DotNotationDict, self).__init__(self._dictionary)

    def __getitem__(self, key):
        item = None
        if '.' in key:
            head, tail = key.split('.', 1)
            item = self._dictionary[head]
            if tail:
                item = DotNotationDict(item)[tail]
        else:
            item = self._dictionary.get(key)
        return item

    def __setitem__(self, key, value):
        if '.' in key:
            head, tail = key.split('.', 1)
            if head not in self._dictionary:
                self._dictionary[head] = {}
                super(DotNotationDict, self).__setitem__(head, {})

            if tail:
                DotNotationDict(self._dictionary[head])[tail] = value
            else:
                self._dictionary[head] = value
                super(DotNotationDict, self).__setitem__(head, value)
        else:
            self._dictionary[key] = value
            super(DotNotationDict, self).__setitem__(key, value)


class BidirectionalDict(dict):  # pylint: disable=too-few-public-methods
    def __init__(self, dictionary=None):
        self._dictionary = dictionary if dictionary else {}
        self._dictionary.update(dict([reversed(i) for i in self._dictionary.items()]))
        super(BidirectionalDict, self).__init__(self._dictionary)

    def __setitem__(self, key, value):
        self._dictionary[key] = value
        self._dictionary[value] = key

    def __delitem__(self, key):
        value = self._dictionary.pop(key)
        self._dictionary.pop(value)
