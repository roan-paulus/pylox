import sys
import os


def main():
    if len(sys.argv) > 2:
        print("Usage: python generate_ast.py <output directory>")
        sys.exit(1)

    output_dir = sys.argv[1]
    visitor_filepath = f"{output_dir}/visitor.py"
    try:
        os.remove(visitor_filepath)
    except FileNotFoundError:
        pass

    define_ast(
        output_dir,
        "Expr",
        [
            "Assign | name: Token, value: Expr",
            "Binary | left: Expr, operator: Token, right: Expr",
            "Ternary | condition: Expr, conditional_operator: Token, left: Expr, branch_operator: Token, right: Expr",
            "Grouping | expression: Expr",
            "Literal | value: object",
            # "Logical | left, operator, right",
            "Unary | operator: Token, right: Expr",
            "Variable | name: Token",
            # "Call | callee, paren_loc, arguments",
            # "Grouping | expression",
            # "Get | object, name",
            # "Set | object, name, value",
            # "Self | keyword",
            # "Super | keyword, method"
        ],
        imports=[
            "from ttoken import Token",
        ]
    )

    define_ast(
        output_dir,
        "Stmt",
        [
            "Block | statements: list[Stmt]",
            "ExprStmt | expression: Expr",
            "Print | expression: Expr",
            "Var | name: Token, initializer: Expr",
            # "If | condition, then_branch, else_branch",
            # "While | condition, body",
            # "Function | name, params, body",
            # "Return | keyword, value",
            # "Class | name, superclass, methods",
        ],
        imports=[
            "from ttoken import Token",
            "from Expr import Expr",
        ]
    )


def define_ast(output_dir, base_name, types, imports=None):
    if imports is None:
        imports = []

    path = output_dir + "/" + base_name + ".py"
    output_file = open(path, "w", encoding="UTF-8")

    define_imports(output_file, imports)
    define_base_class(output_file, base_name)

    visitor_filepath = f"{output_dir}/visitor.py"
    with open(visitor_filepath, "a") as visitor_file:
        define_visitor(visitor_file, base_name, types)

    # the AST classes
    for ttype in types:
        class_name = ttype.split("|")[0].strip()
        fields = ttype.split("|")[1].strip()
        define_type(output_file, base_name, class_name, fields)


def define_base_class(output_file, base_name):
    output_file.write(f"class {base_name}(ABC):\n")
    output_file.write(f"    @abstractmethod\n")
    output_file.write(f"    def accept(self, visitor):\n")
    output_file.write(f"        pass\n")


def define_imports(output_file, imports=None):
    if imports is None:
        imports = []

    output_file.write("from abc import ABC, abstractmethod\n")

    for import_line in imports:
        output_file.write(f"{import_line}\n")

    output_file.write("\n\n")


def visitor_imports(output_file):
    define_imports(output_file)


def define_visitor(visitor_file, base_name, types):
    visitor_file.write(f"from {base_name} import *\n")
    visitor_imports(visitor_file)

    visitor_file.write(f"\nclass {base_name}Visitor(ABC):\n")

    for type_name in types:
        type_name = type_name.split("|")[0].strip()
        visitor_file.write(f"    @abstractmethod\n")
        visitor_file.write(
            f"    def visit_{type_name.lower()}_{base_name.lower()}(self, {base_name.lower()}: {type_name}):\n"
        )
        visitor_file.write(f"        pass\n\n")

    print(f"[written]: {visitor_file.name}")


def define_type(output_file, base_name, class_name, fields):
    output_file.write(f"\nclass {class_name}({base_name}):\n")
    output_file.write(f"    def __init__(self, {fields}):\n")

    # Store parameters in fields
    fields = fields.split(", ")
    for field in fields:
        name = field.split(": ")[0].strip()
        output_file.write(f"        self.{name} = {name}\n")
    output_file.write("\n")

    # Visitor Pattern
    output_file.write(f"    def accept(self, visitor):\n")
    output_file.write(
        f"        return visitor.visit_{class_name.lower()}_{base_name.lower()}(self)\n"
    )


if __name__ == "__main__":
    main()
