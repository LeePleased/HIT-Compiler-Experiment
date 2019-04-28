from utils.load import Token
from model.analysis import EPSILON_SIGN
from model.analysis import TERMINAL_SIGN


class StackInducer(object):

    def __init__(self, table, external):
        self._table = table

        exec("import " + external)
        exec("self._call_list = " + external)

    def generate(self, token_list):
        parse_list, context, table, error_list = [], [], [], []

        stack = BottomStack()
        buffer = BufferStream(token_list)

        # 迭代终止条件: 空栈 + 空缓冲.
        while len(stack) > 2 or buffer.token.category != TERMINAL_SIGN:

            state = stack.state
            token = buffer.token

            result = self._table.query(state, token.category)
            if isinstance(result, int):
                stack.push(token, result)
                buffer.move()
            elif result is not None:
                left, right = result.left, result.right
                parse_list.append(str(result))

                # 如果规约时有语义动作则提前执行.
                if result.in_call is not None:
                    serial = result.in_call.split("-")[-1]
                    exec("self._call_list.call_" + serial + "(stack, buffer, table, context)")

                # 除了空串外, 全部都规约出栈排出.
                for sign in right:
                    if sign != EPSILON_SIGN:
                        stack.pop()

                # 新规约的符号一定是一个非终结符.
                next_state = self._table.query(
                    stack.state, left
                )
                stack.push(Token(left, "-"), next_state)
            else:
                # 基于恐慌模式进行错误规避.
                error_list.append(
                    "字段 <{}> 解析出现问题, 已跳过并继续做语义解析;".format(token)
                )
                buffer.move()

        # 返回规约过程, 生成代码和错误报告.
        return parse_list, context, table, error_list


class BufferStream(object):
    """
    输入 token 的数据流缓冲, 当 category = TERMINAL_SIGN 时结束.
    """

    def __init__(self, token_list):
        self._token_list = token_list + [Token(TERMINAL_SIGN, "-")]
        self._pointer = 0

    @property
    def token(self):
        return self._token_list[self._pointer]

    @property
    def pointer(self):
        return self._pointer

    def get_tok(self, pointer):
        return self._token_list[pointer]

    def move(self):
        if self._pointer < len(self._token_list) - 1:
            self._pointer += 1

    def __str__(self):
        represent = [str(t) for t in self._token_list]
        represent[self._pointer] = "<" + represent[self._pointer] + ">"
        return "| " + " | ".join(represent) + " |"


class BottomStack(object):
    """
    模拟用于转换状态的下推自动机, 其中状态和动作都是栈控
    制的, 而节点属性则是由一个列表 (set/get) 控制的.

    栈顶在列表的 -1 位置, 正好符号 LR 下推规约朝右的方向.
    """

    def __init__(self):
        """
        语义属性完全交由预定义 call_list 管理, 本地函数
        不参与任何的修改, 尽量的解耦这些模块.
        """

        self._token_stack = []
        self._state_stack = []

        # 其中放置字典, 表示节点的属性.
        self._attribute_list = []

        # 初始化栈空间, 放置一个句尾符.
        self.push(Token(TERMINAL_SIGN, "-"), 0)

    @property
    def state(self):
        return self._state_stack[-1]

    @property
    def token(self):
        return self._token_stack[-1]

    @property
    def pointer(self):
        return len(self._state_stack) - 1

    def get_tok(self, position):
        return self._token_stack[position]

    def set_attr(self, position, name, value):
        if len(self._attribute_list) - 1 < position:
            self._attribute_list.append({})

        # 如果属性表不够长则不断填充直至足够.
        self._attribute_list[position][name] = value
        
    def get_attr(self, position, name):
        return self._attribute_list[position][name]

    def clear_attr(self, position):
        self._attribute_list[position] = {}

    def __str__(self):
        represent = [
            str(t) + " " + str(s) + " " + str(d) for t, s, d in
            zip(self._token_stack, self._state_stack, self._attribute_list)
        ]
        return "| " + " | ".join(represent) + " |"

    def push(self, token, state):
        self._token_stack.append(token)
        self._state_stack.append(state)

        # 每次检查属性表是否比栈短, 及时补充.
        while len(self._attribute_list) < len(self._state_stack):
            self._attribute_list.append({})

    def pop(self):
        token = self._token_stack.pop()
        state = self._state_stack.pop()
        return token, state

    def __len__(self):
        return len(self._state_stack)
