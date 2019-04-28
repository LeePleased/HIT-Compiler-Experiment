import os
import json
import argparse

from model import LRReducer, StackInducer
from utils import lexicon_scan, read_grammar, show


parser = argparse.ArgumentParser()

parser.add_argument("--data_dir", "-dd", type=str, default="data")
parser.add_argument("--gui", "-g", action="store_true", default=False)

args = parser.parse_args()
print(json.dumps(args.__dict__, indent=True), end="\n\n")

# 决定是否调用 GUI 例程.
if not args.gui:

    # 做词法分析并推导出错误的信息.
    token_list, lexicon_error = lexicon_scan(
        os.path.join(args.data_dir, "test.c"),
        os.path.join(args.data_dir, "ontology", "lexicon.json")
    )
    grammar_list, terminal_set, phrase_set = read_grammar(
        os.path.join(args.data_dir, "ontology", "grammar.json")
    )

    # 声明 LALR(1) 状态机和下推解析器.
    table_reducer = LRReducer(grammar_list, terminal_set, phrase_set)
    up_inducer = StackInducer(table_reducer, args.data_dir.replace("/", "."))

    # 将词法分析爬取的结果喂入语义分析中.
    print("分析过程中出现的语义分析错误: ")
    parse_list, context, table, semantic_error = up_inducer.generate(token_list)

    print("\n\n分析过程中出现的语法分析错误: ")
    for error in semantic_error:
        print(error)

    print("\n\n分析过程中出现的词法分析错误: ")
    for error in lexicon_error:
        print(error)

    print("\n\n文法 LALR(1) 中语法数的生成过程:")
    for production in parse_list:
        print(production)

    print("\n\n语义分析生成的符号表 (标识属性):")
    print("变量名称\t\t变量类型\t\t字节大小")
    for pair in table:
        print(str(pair[0]) + "\t\t" + str(pair[1]) + "\t\t" + str(pair[2]))

    print("\n\n语义分析生成的中间代码具体流程:")
    for index, command in enumerate(context):
        print("行 {:3d}:\t\t\t".format(index) + command)
else:
    show(LRReducer, StackInducer)
