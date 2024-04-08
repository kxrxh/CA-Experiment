from lark import Lark, Transformer, Tree, v_args
import lark

# Define the assembly language grammar
asm_grammar = r"""
start: instruction+

instruction: label? opcode (operand ("," operand)*)?
label: LABEL
opcode: ADD | SUB | MUL | DIV | LOAD | STORE | JUMP | JMPZ | HALT | MOV | INC
operand: REGISTER | IMMEDIATE | MEMORY_ADDR

LABEL: /[a-zA-Z]+:/
REGISTER: /r\d+/
IMMEDIATE: /[0-9]+/
MEMORY_ADDR: /\[r[0-9]+\]/

ADD: "add"
INC: "inc"
MOV: "mov"
SUB: "sub"
MUL: "mul"
DIV: "div"
LOAD: "load"
STORE: "store"
JUMP: "jmp"
JMPZ: "jmpz"
HALT: "halt"

%ignore /\s+/
"""


# Define the transformer to convert the parsed tree into an AST
@v_args()
class AsmTransformer(Transformer):
    def instruction(self, tree):
        label = None
        opcode = None
        operands = []
        print(tree)
        return {
            "label": label,
            "opcode": opcode,
            "operands": operands
        }

    def label(self, label_name):
        return label_name

    def opcode(self, opcode):
        return opcode

    def operand(self, operand):
        return operand

    def REGISTER(self, reg):
        return reg

    def IMMEDIATE(self, imm: str):
        return int(imm)

    def MEMORY_ADDR(self, addr):
        return int(addr[1:-1])

    def LABEL_NAME(self, label_name):
        return label_name


# Create the Lark parser
asm_parser = Lark(asm_grammar, start="start", parser="lalr",
                  transformer=AsmTransformer())


def main():
    # Example assembly language code
    asm_code = """
    loop:
        mov r0, 1
        add r1, r0
        inc r11
        halt
    """

    # Parse the assembly language code
    ast = asm_parser.parse(asm_code)
    print(ast)


if __name__ == "__main__":
    main()
