import codecs


class Grammar(object):

    def __init__(self, left, right):
        self._left = left
        self._right = right

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    def __str__(self):
        return self._left + " -> " + " ".join(self._right)


def read_grammar(file_path):
    grammar_list = []

    with codecs.open(file_path, "r", encoding="utf-8") as fr:
        for line in fr.readlines():
            pair = line.split("->")

            grammar_list.append(Grammar(
                pair[0].strip(),
                pair[1].strip().split()
            ))
    return grammar_list


def read_code(file_path):
    item_list = []

    with codecs.open(file_path, "r", encoding="utf-8") as fr:
        for line in fr.readlines():
            item_list.extend(line.strip().split())
    return item_list
