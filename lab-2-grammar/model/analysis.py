from model.scan import EPSILON_SIGN
from model.scan import TERMINAL_SIGN


class StackInducer(object):

    def __init__(self, reducer):
        self._reducer = reducer

    def make_inference(self, buffer_list):
        token_buffer = SignBuffer(buffer_list)
        push_stack = StateStack()

        # 一般默认 0 是起始项目集的状态.
        push_stack.push(TERMINAL_SIGN, 0)

        induce_list = []
        while True:

            state = push_stack.state
            token = token_buffer.token

            # 如果返回整数是转移, 否则是规约.
            result = self._reducer.query(state, token)
            if isinstance(result, int):
                push_stack.push(token, result)
                token_buffer.move()
            else:
                left = result.left
                right = result.right

                for _ in range(0, len(right)):
                    push_stack.pop()

                next_state = self._reducer.query(
                    push_stack.state, left
                )
                push_stack.push(left, next_state)
                induce_list.append(str(result))

            # 将栈首和缓冲首部可能出现的符号 pop 掉.
            while push_stack.sign == token_buffer.token:
                push_stack.pop()
                token_buffer.move()

            if push_stack.sign == "SS":
                break

        # 返回所有规约表达式的列表.
        return induce_list


class SignBuffer(object):

    def __init__(self, sign_list):
        self._sign_list = sign_list + [TERMINAL_SIGN]
        self._pointer = 0

    @property
    def token(self):
        return self._sign_list[self._pointer]

    def move(self):
        self._pointer += 1

    def __str__(self):
        return " ".join(self._sign_list)

    def __len__(self):
        return len(self._sign_list)


class StateStack(object):
    """
    模拟用于转换状态的下推自动机.
    """

    def __init__(self):
        self._sign_stack = []
        self._state_stack = []

    @property
    def state(self):
        return self._state_stack[-1]

    @property
    def sign(self):
        return self._sign_stack[-1]

    def push(self, sign, state):
        self._sign_stack.append(sign)
        self._state_stack.append(state)

    def pop(self):
        sign = self._sign_stack.pop()
        state = self._state_stack.pop()
        return sign, state

    def __len__(self):
        return len(self._sign_stack)

    def __str__(self):
        sign = " ".join([str(s) for s in self._sign_stack])
        state = " ".join([str(s) for s in self._state_stack])
        return sign + "\n" + state
