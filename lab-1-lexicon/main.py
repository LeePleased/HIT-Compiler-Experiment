import os
import json
import codecs


def expand_list(n_list):
    f_list = []

    for item in n_list:
        if isinstance(item, (list, tuple)):
            f_list.extend(expand_list(item))
        else:
            f_list.append(item)

    # 返回压平的嵌套列表.
    return f_list


class DataBuffer(object):

    def __init__(self, code_list):
        """
        这里输入是一个二维的字符表. 第一维表示行号, 第二
        维是改行包含的所有字符 (除了空格和空行以外).
        """

        self._code_list = code_list
        self._row_index = 0
        self._column_index = -1

    @property
    def char(self):
        """
        返回 None 表示已经到达文件的末尾了.
        """

        try:
            return self._code_list[self._row_index][self._column_index]
        except IndexError:
            return None

    @classmethod
    def from_file(cls, file_path):
        code_list = []

        with codecs.open(file_path, "r", encoding="utf-8") as fr:
            for line in fr.readlines():

                # 不要去掉空行, 这样至少保证每行一个字符.
                item_list = [list(w) for w in list(line)]
                code_list.append(expand_list(item_list))

        # 从文件构造对象并做返回.
        return cls(code_list)

    def move(self):
        self._column_index += 1

        # 如果列越界则读取下一行的元素.
        if self._column_index == len(self._code_list[self._row_index]):
            self._row_index += 1
            self._column_index = 0

    def back(self):
        self._column_index -= 1

        # 如果列越界则回退去读上一行.
        if self._column_index < 0:
            self._row_index -= 1
            self._column_index = len(self._code_list[self._row_index]) - 1

    def lexical_error(self, message):
        return message + " in " + "<line: {:3d}, index: {:3d}>".format(self._row_index, self._column_index)

    def __str__(self):
        return str(self._code_list)


def lexicon_scanning(code_path, ontology_path):
    buffer = DataBuffer.from_file(code_path)

    with codecs.open(ontology_path, "r", encoding="utf-8") as fr:
        ontology = json.load(fr)

    # 以二元组的形式存储爬取的结果.
    parse_list, error_list = [], []

    while buffer.char:
        buffer.move()

        # 如果没有输入了则退出.
        if buffer.char is None:
            break

        # 识别整数或者浮点数.
        if buffer.char.isdigit():
            int_value = 0
            while buffer.char.isdigit():
                int_value = int_value * 10 + int(buffer.char)
                buffer.move()

            if buffer.char != ".":
                buffer.back()
                parse_list.append(("INT", str(int_value)))
                continue

            float_value = str(int_value) + "."
            buffer.move()
            while buffer.char.isdigit():
                float_value += buffer.char
                buffer.move()
            buffer.back()

            parse_list.append(("FLOAT", str(float_value)))
            continue

        # 识别标识符或者关键字.
        if buffer.char.isalpha() or buffer.char == "_":
            string = ""

            while buffer.char.isalpha() or buffer.char.isdigit() or buffer.char == "_":
                string += buffer.char
                buffer.move()
            buffer.back()

            if string in ontology["keyword"]:
                parse_list.append((string, "-"))
            else:
                parse_list.append(("ID", string))
            continue

        # 识别出代码中的分隔符.
        if buffer.char in ontology["separator"]:
            parse_list.append(("SEP", buffer.char))
            continue

        # 识别出代码中的操作数.
        if buffer.char in ontology["operator"]:
            operator = buffer.char

            buffer.move()
            next_char = buffer.char

            if next_char in ontology["operator"]:
                operator += next_char
            else:
                buffer.back()

            parse_list.append(("OP", operator))
            continue

        # 如果以上情况都不满足则是错误的字符.
        if buffer.char.strip() != "":
            error_list.append(buffer.lexical_error("unknown character: {}".format(buffer.char)))

    # 按元组 (类別, 符号) 的列表返回.
    return parse_list, error_list


if __name__ == "__main__":
    data_path = "./data"

    result, error = lexicon_scanning(
        os.path.join(data_path, "test.c"),
        os.path.join(data_path, "ontology.json")
    )

    if len(error) != 0:
        print("词法分析出现的错误信息:")
        for err_str in error:
            print(err_str)
        print("\n")

    print("词法器爬取的类型和词汇如下:")
    for pair in result:
        print(pair[0] + "\t\t\t\t\t\t\t" + str(pair[1]))
