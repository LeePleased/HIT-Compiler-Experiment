"""
目前默认用 ### 表示空串, 但最好不要用它.
"""

from copy import deepcopy


EPSILON_SIGN = "###"
TERMINAL_SIGN = "$$$"


class Project(object):
    """
    文法 LR(1) 特有的项目, 包装了 Grammar 类, 想比起一
    般的语法生成式多了一个规约状态位和一个展望符.
    """

    def __init__(self, grammar, position, token):
        self._grammar = grammar
        self._position = position
        self._token = token

    @property
    def grammar(self):
        return self._grammar

    @property
    def position(self):
        return self._position

    @property
    def token(self):
        return self._token

    def move(self):
        return Project(
            grammar=self._grammar,
            position=self._position + 1,
            token=self._token
        )

    def __str__(self):
        """
        用 __str__ 判断两个项目是否是等同的.
        """

        return "|| " + " || ".join([
            str(self._grammar),
            str(self._position),
            self._token]
        ) + " ||"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return str(self) == str(other)

    def __ge__(self, other):
        return str(self) > str(other)

    def __hash__(self):
        return hash(str(self))


class LRReducer(object):
    """
    基于 LR(1) 规约的文法对象, 用于建预测分析表.
    """

    def __init__(self, grammar_list, terminal_set, phrase_set):
        self._grammar_list = grammar_list
        self._terminal_set = terminal_set
        self._phrase_set = phrase_set

        self._look_up = LookUpTable(
            grammar_list, terminal_set, phrase_set
        )

        self._move_table = None
        self._family_list = None
        self._build()

    def query(self, state, token):
        """
        如果查询不存在则返回一个 None.
        """

        try:
            return self._move_table[state][token]
        except KeyError:
            return None

    def _build(self):
        self._move_table = {}

        self._family_list = [self._closure({Project(
            self._grammar_list[0], 0, TERMINAL_SIGN
        )})]

        # 只要还有新建的项目就继续 goto.
        while True:
            update_list = []

            for index, family in enumerate(self._family_list):
                if index not in self._move_table.keys():
                    self._move_table[index] = {}

                # 这里连接状态表不考虑空串和语句结尾符.
                for sign in self._terminal_set.union(self._phrase_set):
                    if sign in [EPSILON_SIGN, TERMINAL_SIGN]:
                        continue

                    # 给定项目集族和转移符号做状态转移.
                    next_family = self._goto(family, sign)

                    # 仅当下一步 goto 产生的项集是非空的.
                    if len(next_family) == 0:
                        continue

                    # 如果新产生的项集在其他的状态中出现过.
                    flag, next_index = True, None
                    for serial, other in enumerate(self._family_list):
                        if next_family.issubset(other):
                            next_index, flag = serial, False
                            break

                    if flag:
                        next_index = len(self._family_list) + len(update_list)
                        update_list.append(next_family)
                    self._move_table[index][sign] = next_index

            if len(update_list) > 0:
                self._family_list.extend(update_list)
            else:
                break

        # 文法 LR(1) 允许同一个状态既存在规约, 又存在生成.
        for index, family in enumerate(self._family_list):
            for project in family:
                if project.position == len(project.grammar):
                    self._move_table[index][project.token] = project.grammar

    def _closure(self, project_set):
        """
        自增形的闭包要避免循环自调用, 否则报错.
        """

        buffer_set = deepcopy(project_set)
        while True:

            for project in project_set:
                grammar = project.grammar
                position = project.position
                token = project.token

                # 如果该项目已完成规约, 则无需递归了.
                assert position <= len(grammar)
                if position == len(grammar):
                    continue

                current = grammar.right[position]
                suffix = grammar.right[position + 1:]

                # 如果其指向是终结符则只能等待 goto.
                if current in self._terminal_set:
                    continue

                for candidate in self._grammar_list:
                    if candidate.left == current:
                        first_set = self._look_up.get_first_set(
                            suffix + [token]
                        )

                        # 方法 __eq__ 避免向闭包中增加重复的元素.
                        for first in first_set:

                            # 这里不考虑空串的展望符.
                            if first == EPSILON_SIGN:
                                continue
                            buffer_set.add(Project(candidate, 0, first))

            if len(buffer_set) == len(project_set):
                break
            project_set = deepcopy(buffer_set)

        return project_set

    def _goto(self, project_set, sign):
        next_family = set()

        for project in project_set:
            grammar = project.grammar
            position = project.position

            # 如果该项目已完成规约, 则无需转移了.
            assert position <= len(grammar)
            if position == len(grammar):
                continue

            if grammar.right[position] == sign:
                next_family.add(project.move())

        expand_f = self._closure(next_family)
        return expand_f


class LookUpTable(object):
    """
    维护 first 和 follow 两种映射表并提供方法.
    """

    def __init__(self, grammar_list, terminal_set, phrase_set):
        """
        串首终结符集, 非终结符的后继符号集.
        """

        self._terminal_set = terminal_set
        self._phrase_set = phrase_set
        self._first_map, self._follow_map = {}, {}

        # 根据语法构建 first 和 follow 集.
        self._build_first_table(grammar_list)
        self._build_follow_table(grammar_list)

    def _build_first_table(self, grammar_list):
        buffer_map = dict()

        # 在 first 中增加两个特别的符号.
        buffer_map[TERMINAL_SIGN] = {TERMINAL_SIGN}
        buffer_map[EPSILON_SIGN] = {EPSILON_SIGN}

        # 终结符号的 first 集就是本身.
        for item in self._terminal_set:
            buffer_map[item] = {item}
        for item in self._phrase_set:
            buffer_map[item] = set()

        # 如果能够推导出空串, 也将其加入集合.
        for grammar in grammar_list:
            if grammar.right == [EPSILON_SIGN]:
                buffer_map[grammar.left].add(EPSILON_SIGN)

        # 闭包推导是相当于那些非终结符而言的.
        while True:
            for item in self._phrase_set:

                for grammar in grammar_list:
                    if grammar.left != item:
                        continue

                    for sub_i in grammar.right:
                        buffer_map[item] = buffer_map[item].union(buffer_map[sub_i])

                        # 如果之前的符号不能推导出空串, 则退出.
                        if EPSILON_SIGN not in buffer_map[sub_i]:
                            break

            # 如果没有新增的元素则退出, 否则更新 first.
            if dict_size(buffer_map) == dict_size(self._first_map):
                break
            self._first_map = deepcopy(buffer_map)

    def _build_follow_table(self, grammar_list):
        buffer_map = {}

        # 后继符号集是相对于非终端符而言的.
        for item in self._phrase_set:
            buffer_map[item] = set()

        # 避免错误, 可能存在一些不完备的文法.
        for grammar in grammar_list:
            buffer_map[grammar.left] = {TERMINAL_SIGN}

        while True:
            for grammar in grammar_list:

                for index in range(0, len(grammar.right) - 1):
                    current = grammar.right[index]

                    if current in self._phrase_set:
                        first_set = self.get_first_set(
                            grammar.right[index + 1:]
                        )

                        # 将 first_set 中的空字符串除去.
                        try:
                            first_set.remove(EPSILON_SIGN)
                        except KeyError:
                            pass
                        buffer_map[current] = buffer_map[current].union(first_set)

                for index in range(0, len(grammar.right))[::-1]:
                    current = grammar.right[index]

                    if current in self._phrase_set:
                        follow_set = buffer_map[grammar.left]
                        buffer_map[current] = buffer_map[current].union(follow_set)

                    first_set = self._first_map[current]
                    if EPSILON_SIGN not in first_set:
                        break

            if dict_size(buffer_map) == dict_size(self._follow_map):
                break
            self._follow_map = deepcopy(buffer_map)

    def get_first_set(self, item_list):
        first_set = set()

        for item in item_list:
            first_set = first_set.union(self._first_map[item])

            # 如果不能获取连续的空串则退出.
            if EPSILON_SIGN not in self._first_map[item]:
                break
        return first_set

    def get_follow_set(self, item):
        return self._follow_map[item]


def dict_size(i_dict):
    total_len = 0

    for val_list in i_dict.values():
        total_len += len(val_list)
    return total_len
