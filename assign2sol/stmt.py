# <your name>
#
# CS358 Fall '25 Assignment 2
#
# Stmt - A small statement language with assignments, conditionals,
#        loops, print statements, and block statements.

from lark import Lark, v_args
from lark.visitors import Interpreter

grammar = """
    ?start: stmt

    ?stmt: ID "=" expr                          -> assign
         | "if" "(" expr ")" stmt ["else" stmt] -> if_stmt
         | "while" "(" expr ")" stmt            -> while_stmt
         | "print" "(" expr ")"                 -> print_stmt
         | "{" stmt (";" stmt)* "}"             -> block

    ?expr: expr "+" term                        -> add
         | expr "-" term                        -> sub
         | term

    ?term: term "*" atom                        -> mul
         | term "/" atom                        -> div
         | atom

    ?atom: "(" expr ")"
         | ID                                   -> var
         | NUM                                  -> num

    %import common.WORD   -> ID
    %import common.INT    -> NUM
    %import common.WS
    %ignore WS
"""

parser = Lark(grammar, parser="lalr", start="start")


@v_args(inline=True)
class Eval(Interpreter):
    """
    Interpreter for the Stmt language.

    - The environment (env) is a dictionary mapping variable names to integer values.
    - All variables default to 0 if not previously assigned.
    - Expressions evaluate to integer values.
    - Statements update env or perform side effects (such as printing).
    """
    def __init__(self):
        self.env = {}  # Global variable environment

    # -------------------------
    # Atomic Expression Values
    # -------------------------
    def num(self, tok):
        return int(tok)

    def var(self, name):
        # Return variable value, defaulting to 0 if undefined
        return self.env.get(str(name), 0)

    # -------------------------
    # Arithmetic Operations
    # -------------------------
    def add(self, x, y): return self.visit(x) + self.visit(y)
    def sub(self, x, y): return self.visit(x) - self.visit(y)
    def mul(self, x, y): return self.visit(x) * self.visit(y)

    def div(self, x, y):
        # Integer division with error handling
        denom = self.visit(y)
        if denom == 0:
            raise ZeroDivisionError("Division by zero")
        return self.visit(x) // denom

    # -------------------------
    # Statement Execution
    # -------------------------
    def assign(self, name, expr):
        # Evaluate expression and store result in variable
        val = self.visit(expr)
        self.env[str(name)] = val

    def print_stmt(self, expr):
        # Evaluate and output the result
        val = self.visit(expr)
        print(val)

    def if_stmt(self, cond, then_stmt, else_stmt=None):
        # Execute then-branch if condition is non-zero, else execute else-branch if present
        if self.visit(cond) != 0:
            self.visit(then_stmt)
        elif else_stmt is not None:
            self.visit(else_stmt)

    def while_stmt(self, cond, body):
        # Execute body repeatedly while condition evaluates to non-zero
        while self.visit(cond) != 0:
            self.visit(body)

    def block(self, first_stmt, *rest):
        # Execute statements in sequence inside a block
        self.visit(first_stmt)
        for stmt in rest:
            self.visit(stmt)


# -------------------------
# Simple REPL for Testing
# -------------------------
def main():
    import sys

    if len(sys.argv) == 2:
        # Run a file given as argument: python stmt.py program.st
        with open(sys.argv[1]) as f:
            prog = f.read()
    else:
        # Otherwise ask user for input
        prog = input("Enter a program: ")

    try:
        tree = parser.parse(prog)
        Eval().visit(tree)
    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
