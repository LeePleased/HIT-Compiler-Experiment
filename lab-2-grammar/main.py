import os
import json
import argparse

from model import LRReducer, StackInducer
from utils import read_code, read_grammar


parser = argparse.ArgumentParser()
parser.add_argument("--data_dir", "-dd", type=str, default="./data")

args = parser.parse_args()
print(json.dumps(args.__dict__, indent=True), end="\n\n")

# 读入代码 (token 的种类的列表) 和语法.
item_list = read_code(os.path.join(args.data_dir, "test.txt"))
grammar_list = read_grammar(os.path.join(args.data_dir, "grammar.txt"))

reducer = LRReducer(grammar_list)
analyze = StackInducer(reducer)

result = analyze.make_inference(item_list)
for item in result:
    print(item)
