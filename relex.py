# relex.py
# Son Phan
#
# CS358 Fall '25 Assignment 2
#
# RelEx - a language consisting only of relational comparison operators
#
#   relex -> relex rop atom
#         |  atom
#   atom  -> "(" relex ")"
#         |  NUM
#   rop   -> "<"|"<="|">"|">="|"=="|"!="
#
from lark import Lark, v_args, Tree, Token
from lark.visitors import Interpreter

# ----------------------------
# 1) Lark Grammar for RelEx
# ----------------------------
# - Attach AST labels:
#     relex rop atom -> binop
#     "(" relex ")"  -> paren
#     NUM             -> num
# - Keep rop as a rule as required.
grammar = r"""
    ?start: relex

    ?relex: relex ROP atom      -> binop
          | atom

    atom : "(" relex ")"        -> paren
         | NUM                  -> num

    ROP: "<=" | "<" | ">=" | ">" | "==" | "!="

    %import common.INT      -> NUM
    %import common.WS
    %ignore WS
"""

# Using LALR (fast and suitable for LR grammars like this one)
parser = Lark(grammar, parser="lalr", start="relex")


# ---------------------------------------------------
# 2) Helper Functions
# ---------------------------------------------------
def _op_text(op_token):
    return str(op_token)


def _cmp(op: str, a, b):
    """
    Perform the comparison a (op) b.
    Returns a boolean True/False.
    EvalC() will convert this to 0/1.
    EvalP() uses it directly.
    """
    if op == "<":
        return a < b
    if op == "<=":
        return a <= b
    if op == ">":
        return a > b
    if op == ">=":
        return a >= b
    if op == "==":
        return a == b
    if op == "!=":
        return a != b
    raise ValueError(f"Invalid operator: {op}")


# -----------------------------------------
# 3) EvalC — Interpreter with C Semantics
# -----------------------------------------
# - Chained comparisons are evaluated left-to-right,
#   i.e., (a < b) < c ...
# - Comparison results become integers:
#     true -> 1, false -> 0
@v_args(inline=True)
class EvalC(Interpreter):
    def num(self, tok: Token):
        return int(tok)

    def paren(self, expr):
        return self.visit(expr)

    def binop(self, left, op_node, right):
        left_val = self.visit(left)
        right_val = self.visit(right)
        op = _op_text(op_node)
        return int(_cmp(op, left_val, right_val))

# Testing 

# -----------------------------------------
# 4) EvalP — Interpreter with Python Semantics
# -----------------------------------------
# - Chained comparisons replicate the middle operand:
#       a < b < c   →   (a < b) and (b < c)
# - We must manually detect if the left side is itself another binop.
# - Returns True/False.
@v_args(inline=True)
class EvalP(Interpreter):
    def num(self, tok: Token):
        return int(tok)

    def paren(self, expr):
        return self.visit(expr)

    def binop(self, left, op_node, right):
        # Flatten the chain of binops
        def flatten_binop(tree):
            if isinstance(tree, Tree) and tree.data == "binop":
                left, op_node, right = tree.children
                return flatten_binop(left) + [(op_node, right)]
            else:
                return [(None, tree)]

        chain = flatten_binop(Tree("binop", [left, op_node, right]))

        # Evaluate the chain
        for i in range(1, len(chain)):
            _, left_expr = chain[i - 1]
            op_node, right_expr = chain[i]
            op = _op_text(op_node)
            left_val = self.visit(left_expr)
            right_val = self.visit(right_expr)
            if not _cmp(op, left_val, right_val):
                return False
        return True
# ----------------------------
# 5) Small REPL for Testing
# ----------------------------
def main():
    while True:
        try:
            prog = input("Enter an expr: ")
            if not prog.strip():
                continue
            tree = parser.parse(prog)
            print("\n== Parse Tree ==")
            print(tree.pretty(), end="")

            ec = EvalC().visit(tree)
            ep = EvalP().visit(tree)
            print("\n== Results ==")
            print("EvalC:", ec)   # integer 0 or 1
            print("EvalP:", ep)   # Python boolean
            print()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        except Exception as e:
            print("Error:", e)
            print()

if __name__ == "__main__":
    main()
