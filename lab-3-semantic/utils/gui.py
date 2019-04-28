import os
import codecs
import tkinter as tk
from tkinter.filedialog import askdirectory

from utils.load import lexicon_scan
from utils.load import read_grammar

WINDOW_HEIGHT = 1200
WINDOW_WIDTH = 400

root = tk.Tk()
root.title("中间代码生成界面")
root.geometry("{}x{}".format(WINDOW_HEIGHT, WINDOW_WIDTH))

left_text = tk.Text(root, width=int(WINDOW_WIDTH * 0.19), height=WINDOW_HEIGHT)
right_text = tk.Text(root, width=int(WINDOW_WIDTH * 0.19), height=WINDOW_HEIGHT)


def show(translator, generator):
    global WINDOW_HEIGHT, WINDOW_WIDTH
    global root, left_text, right_text

    # 在 load 和 parse 中共享部分变量.
    work_dir, stack = None, None

    def load():
        global work_dir, stack

        work_dir = askdirectory(initialdir="./")
        left_text.delete(1.0, tk.END)
        right_text.delete(1.0, tk.END)

        test_file = os.path.join(work_dir, "test.c")
        with codecs.open(test_file, "r", encoding="utf-8") as fr:
            left_text.insert(tk.INSERT, fr.read())

        right_text.insert(tk.INSERT, "System is building ...")
        grammar, terminal, phrase = read_grammar(
            os.path.join(work_dir, "ontology", "grammar.json")
        )
        table = translator(grammar, terminal, phrase)

        stack_dir = "/".join(work_dir.split("/")[-1:])
        stack = generator(table, stack_dir.replace("/", "."))

        right_text.delete(1.0, tk.END)
        right_text.insert(tk.INSERT, "Ready for analysis.")

    def parse():
        global work_dir, stack
        right_text.delete(1.0, tk.END)

        token, _ = lexicon_scan(
            os.path.join(work_dir, "test.c"),
            os.path.join(work_dir, "ontology", "lexicon.json")
        )

        _, context, _, _ = stack.generate(token)
        for index, command in enumerate(context):
            right_text.insert(tk.INSERT, "Line {:3d}:\t\t\t".format(index) + command + "\n")

    up_button = tk.Button(text="Import Dir", command=load)
    low_button = tk.Button(text="Start Parse", command=parse)

    left_text.pack(side=tk.LEFT)
    right_text.pack(side=tk.RIGHT)
    up_button.pack(side=tk.TOP, pady=int(WINDOW_HEIGHT * 0.07))
    low_button.pack(side=tk.BOTTOM, pady=int(WINDOW_HEIGHT * 0.07))

    root.mainloop()
