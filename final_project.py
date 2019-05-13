import re

LITERAL, PLUS, MINUS, MUL, DIV, LPAREN, RPAREN, EOF = (
    'LITERAL', 'PLUS', 'MINUS', 'MUL', 'DIV', '(', ')', 'EOF'
)


###########
## TOKEN ##
###########

class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):

        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()


###########
## LEXER ##
###########

class Lexer(object):
    def __init__(self, text):
        
        self.text = text
        self.pos = 0 #index of text
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    def advance(self):

        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  #end of input
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):

        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def get_next_token(self):
        
        #breaking onto tokens 
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(LITERAL, self.integer())

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(MUL, '*')

            if self.current_char == '/':
                self.advance()
                return Token(DIV, '/')

            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')

            self.error()

        return Token(EOF, None)


#################
## TREE PARSER ##
#################

class Tree(object):
    pass


class BinOp(Tree):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Num(Tree):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):

        # factor : literal | ( expr ) | - factor | + factor

        token = self.current_token
        if token.type == LITERAL:
            self.eat(LITERAL)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node

    #    elif token.type == MINUS:
    #   self.eat(MINUS)
    #   node = BinOp(left= -1, op=MUL, right = self.factor())
    #   return node
    # elif token.type == PLUS:
    #   self.eat(PLUS)
    #   node = BinOp(left= 1, op=MUL, right = self.factor())
    #   return node

    def term(self):

        # term : term * fact | term / fact | fact

        node = self.factor()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def expr(self):

        # expr : term + exp | term - exp | term

        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)

            node = BinOp(left=node, op=token, right=self.term())

        return node

    def parse(self):
        return self.expr()


#################
## INTERPRETER ##
#################

class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser

    def visit_BinOp(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == DIV:
            return self.visit(node.left) // self.visit(node.right)

    def visit_Num(self, node):
        return node.value

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)

    def validateAndParse(text):

        if (text[len(text) - 1] != ';'):
            print("semicolon ';' missing ")
            exit()
        listOfVariables = list()
        listOfValues = list()

        stmts = text.split(';')
        stmtsCount = len(stmts) - 1
        if (stmtsCount == 0):
            print('incorrect syntax')
            exit()

        for x in range(0, stmtsCount):
            assignment = stmts[x].split()

            if (assignment.pop(1) == '='):
                listOfVariables.append(assignment.pop(0))

                for k in range(0, len(assignment)):
                    match = re.search(r'^[a-z]+', assignment[k])
                    if match:
                        i = listOfVariables.index(assignment[k]) if assignment[k] in listOfVariables else None

                        if i is None:
                            print('The variable -> ', assignment[k], ' <- was not defined. ')
                            exit()
                        else:
                            assignment[k] = listOfValues[i]

                text = ' '.join(str(x) for x in assignment)
                lexer = Lexer(text)
                parser = Parser(lexer)
                interpreter = Interpreter(parser)
                result = interpreter.interpret()
                listOfValues.append(result)
            else:
                print("Assignment '=' was not defined")
                exit()

        return listOfVariables, listOfValues


def main():
    try:
        # separate all symbols with space.
        # to test with different values change the programInput variable

        programInput = 'x_2 = (4 - 2) * 3; y = 5 / x_2 - 4 * ( x_2 - 10 ); m = y * 10; k = 7; d = ( 7 - y ) * ( x_2 + m );'

        # uncomment the bottom line to type in program though the keyboard
        # programInput = input('Enter the program. Separate symbols with spaces: ')

        listOfVariables, listOfValues = Interpreter.validateAndParse(programInput)
        for x in range(0, len(listOfVariables)):
            print(listOfVariables[x], " = ", listOfValues[x])
    except:
        print('incorrent syntax. try again.')


if __name__ == '__main__':
    main()