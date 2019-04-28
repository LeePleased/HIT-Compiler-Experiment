"""
这个文件用于定义语法文件 ontology/grammar.json 中需
要的语义动作函数, 每个函数都有 stack 和 context 两个
参数, 分别表示对调用栈的操作和中间输出结果的列表.
"""


def call_1(stack, buffer, table, context):
    context.append("Wake up (1) !")

    pointer = stack.pointer
    stack.set_attr(pointer + 1, "T'inh", stack.get_attr(pointer, "val"))


def call_2(stack, buffer, table, context):
    context.append("Wake up (2) !")

    pointer = stack.pointer
    stack.set_attr(pointer - 2, "val", stack.get_attr(pointer, "syn"))


def call_3(stack, buffer, table, context):
    context.append("Wake up (3) !")
    pointer = stack.pointer

    left = stack.get_attr(pointer - 2, "T'inh")
    right = stack.get_attr(pointer, "val")
    stack.set_attr(pointer + 1, "T'inh", left * right)


def call_4(stack, buffer, table, context):
    context.append("Wake up (4) !")

    pointer = stack.pointer
    stack.set_attr(pointer - 3, "syn", stack.get_attr(pointer, "syn"))


def call_5(stack, buffer, table, context):
    context.append("Wake up (5) !")

    pointer = stack.pointer
    stack.set_attr(pointer + 1, "syn", stack.get_attr(pointer, "T'inh"))


def call_6(stack, buffer, table, context):
    context.append("Wake up (6) !")

    pointer = stack.pointer
    stack.set_attr(pointer, "val", int(stack.get_tok(pointer).value))
