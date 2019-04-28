"""
这个文件用于定义语法文件 ontology/grammar.json 中需要的语
义动作函数. 这个文件的编写可以结合 debug 和文法来构造.
"""


def call_21(stack, buffer, table, context):
    pointer = stack.pointer

    stack.set_attr(pointer, "type", stack.get_attr(pointer, "type"))
    stack.set_attr(pointer, "length", stack.get_attr(pointer, "length"))


def call_22(stack, buffer, table, context):
    pointer = stack.pointer

    table.append((
        stack.get_attr(pointer, "name"),
        stack.get_attr(pointer, "type"),
        stack.get_attr(pointer, "length")
    ))


def call_31(stack, buffer, table, context):
    pointer = stack.pointer
    stack.set_attr(pointer - 1, "name", stack.get_tok(pointer).value)


def call_91(stack, buffer, table, context):
    stack_pointer = stack.pointer
    buffer_pointer = buffer.pointer

    while True:
        token = buffer.get_tok(buffer_pointer)

        if token.category == "ID":
            break
        buffer_pointer -= 1

        if buffer_pointer == 0:
            print("循环条件语句分析错误.")
            return

    context.append("IF " + token.value + " GOTO " + str(len(context) + 2))
    stack.set_attr(stack_pointer - 1, "back", len(context) - 1)


def call_92(stack, buffer, table, context):
    pointer = stack.pointer

    prev = stack.get_attr(pointer - 3, "back")
    context.insert(prev + 1, "GOTO " + str(len(context) + 2))

    # 需要注意 while 语句还有跳回的操作.
    context.append("GOTO " + str(prev))


def call_81(stack, buffer, table, context):
    stack_pointer = stack.pointer
    buffer_pointer = buffer.pointer

    while True:
        token = buffer.get_tok(buffer_pointer)

        if token.category == "ID":
            break
        buffer_pointer -= 1

        if buffer_pointer == 0:
            print("条件跳转语句分析错误.")
            return 

    context.append("IF " + token.value + " GOTO " + str(len(context) + 2))
    stack.set_attr(stack_pointer - 1, "back", len(context) - 1)


def call_82(stack, buffer, table, context):
    pointer = stack.pointer

    prev = stack.get_attr(pointer - 3, "back")
    context.insert(prev + 1, "GOTO " + str(len(context) + 1))


def call_11(stack, buffer, table, context):
    pointer = stack.pointer

    stack.set_attr(pointer, "type", "int")
    stack.set_attr(pointer, "length", 4)


def call_12(stack, buffer, table, context):
    pointer = stack.pointer

    stack.set_attr(pointer, "type", "float")
    stack.set_attr(pointer, "length", 4)


def call_13(stack, buffer, table, context):
    pointer = stack.pointer

    stack.set_attr(pointer, "type", "double")
    stack.set_attr(pointer, "length", 8)


def call_14(stack, buffer, table, context):
    pointer = stack.pointer

    stack.set_attr(pointer, "type", "short")
    stack.set_attr(pointer, "length", 2)


def call_15(stack, buffer, table, context):
    pointer = stack.pointer

    stack.set_attr(pointer, "type", "long")
    stack.set_attr(pointer, "length", 4)


def call_41(stack, buffer, table, context):
    pointer = stack.pointer

    token = stack.get_tok(pointer)
    stack.set_attr(
        pointer, "value", int(token.value)
    )
    stack.set_attr(pointer, "type", "int")


def call_42(stack, buffer, table, context):
    pointer = stack.pointer

    token = stack.get_tok(pointer)
    stack.set_attr(
        pointer, "value", float(token.value)
    )
    stack.set_attr(pointer, "type", "float")


def call_43(stack, buffer, table, context):
    pointer = stack.pointer

    token = stack.get_tok(pointer)
    stack.set_attr(
        pointer, "value", int(token.value)
    )
    stack.set_attr(pointer, "type", "short")


def call_44(stack, buffer, table, context):
    pointer = stack.pointer

    token = stack.get_tok(pointer)
    stack.set_attr(
        pointer, "value", int(token.value)
    )
    stack.set_attr(pointer, "type", "long")


def call_61(stack, buffer, table, context):
    pointer = stack.pointer
    factor, left, right = pointer, pointer - 4, pointer - 2

    # 搜索符号表, 检查数据类型和是否定义.
    flag = False
    for element in table:
        if element[0] == stack.get_tok(left).value:
            flag = True

            if element[1] != stack.get_attr(right, "type"):
                print("符号 {} 类型错误;".format(stack.get_tok(left).value))
                return
    if not flag:
        print("符号 {} 未定义错误;".format(stack.get_tok(left).value))
        return

    # 检查是否有运算, 若有则计算结果并记录.
    try:
        operator = stack.get_attr(factor, "op")

        if operator == "+":
            result = stack.get_attr(left, "value") + stack.get_attr(factor, "factor")
        elif operator == "-":
            result = stack.get_attr(left, "value") - stack.get_attr(factor, "factor")
        else:
            result = stack.get_attr(left, "value") * stack.get_attr(factor, "factor")

    except KeyError:
        result = stack.get_attr(right, "value")

    stack.clear_attr(factor)
    context.append(stack.get_tok(left).value + " := " + str(result))


def call_62(stack, buffer, table, context):
    pointer = stack.pointer

    stack.set_attr(
        pointer - 2, "type", stack.get_attr(pointer, "type")
    )
    stack.set_attr(
        pointer - 2, "value", stack.get_attr(pointer, "value")
    )


def call_101(stack, buffer, table, context):
    pointer = stack.pointer

    stack.set_attr(
        pointer - 1, "op", stack.get_tok(pointer - 1).category
    )
    stack.set_attr(
        pointer - 1, "factor", stack.get_attr(pointer, "value")
    )


def call_102(stack, buffer, table, context):
    pointer = stack.pointer

    stack.set_attr(
        pointer - 1, "op", stack.get_tok(pointer - 1).category
    )
    stack.set_attr(
        pointer - 1, "factor", stack.get_attr(pointer, "value")
    )


def call_51(stack, buffer, table, context):
    pass


def call_52(stack, buffer, table, context):
    pointer = stack.pointer

    stack.set_attr(
        pointer, "type", stack.get_attr(pointer, "type")
    )
    stack.set_attr(
        pointer, "value", stack.get_attr(pointer, "value")
    )


def call_71(stack, buffer, table, context):
    pointer = stack.pointer

    stack.set_attr(
        pointer, "type", stack.get_attr(pointer, "type")
    )
    stack.set_attr(
        pointer, "value", stack.get_attr(pointer, "value")
    )


def call_72(stack, buffer, table, context):
    pointer = stack.pointer

    stack.set_attr(
        pointer, "type", stack.get_attr(pointer, "type")
    )
    stack.set_attr(
        pointer, "value", stack.get_attr(pointer, "value") + 1
    )


def call_73(stack, buffer, table, context):
    pointer = stack.pointer

    stack.set_attr(
        pointer, "type", stack.get_attr(pointer, "type")
    )
    stack.set_attr(
        pointer, "value", stack.get_attr(pointer, "value") - 1
    )
