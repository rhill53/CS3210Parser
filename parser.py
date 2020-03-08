"""
CS3210 programming project 1
Authors:
    Robb Hill
    Thyago Mota
    Referenced sources
"""

# Skeleton of code below pulled from:
# https://github.com/thyagomota/20SCS3210.git

# CS 3210 - Principles of Programming Languages - Spring 2020
# A bottom-up parser for an expression

from enum import IntEnum
import sys

# enables parser's debugging
DEBUG = True

# all char classes
class CharClass(IntEnum):
    EOF        = -1
    LETTER     = 1
    DIGIT      = 2
    OPERATOR   = 3
    PUNCTUATOR = 4
    QUOTE      = 5
    BLANK      = 6
    DELIMITER  = 7
    OTHER      = 8

# all tokens
class Token(IntEnum):
    EOF             = 0
    INT_TYPE        = 1
    MAIN            = 2
    OPEN_PAR        = 3
    CLOSE_PAR       = 4
    OPEN_CURLY      = 5
    CLOSE_CURLY     = 6
    OPEN_BRACKET    = 7
    CLOSE_BRACKET   = 8
    COMMA           = 9
    ASSIGNMENT      = 10
    SEMICOLON       = 11
    IF              = 12
    ELSE            = 13
    WHILE           = 14
    OR              = 15
    AND             = 16
    EQUALITY        = 17
    INEQUALITY      = 18
    LESS            = 19
    LESS_EQUAL      = 20
    GREATER         = 21
    GREATER_EQUAL   = 22
    ADD             = 23
    SUBTRACT        = 24
    MULTIPLY        = 25
    DIVIDE          = 26
    BOOL_TYPE       = 27
    FLOAT_TYPE      = 28
    CHAR_TYPE       = 29
    IDENTIFIER      = 30
    INT_LITERAL     = 31
    TRUE            = 32
    FALSE           = 33
    FLOAT_LITERAL   = 34
    CHAR_LITERAL    = 35

# a tree-like data structure
class Tree:

    TAB = "   "

    def __init__(self):
        self.data     = None
        self.children = []

    def add(self, child):
        self.children.append(child)

    def print(self, tab = ""):
        if self.data != None:
            print(tab + self.data)
            tab += self.TAB
            for child in self.children:
                if isinstance(child, Tree):
                    child.print(tab)
                else:
                    print(tab + child)

# error code to message conversion function
def errorMessage(code):
    msg = "Error " + str(code).zfill(2) + ": "
    if code == 1:
        return msg + "Source file missing"
    if code == 2:
        return msg + "Couldn't open source file"
    if code == 3:
        return msg + "Lexical error"
    if code == 4:
        return msg + "Digit expected"
    if code == 5:
        return msg + "Symbol missing"
    if code == 6:
        return msg + "EOF expected"
    if code == 7:
        return msg + "'}' expected"
    if code == 8:
        return msg + "'{' expected"
    if code == 9:
        return msg + "')' expected"
    if code == 10:
        return msg + "'(' expected"
    if code == 11:
        return msg + "main expected"
    if code == 12:
        return msg + "int type expected"
    if code == 13:
        return msg + "']' expected"
    if code == 14:
        return msg + "int literal expected"
    if code == 15:
        return msg + "'[' expected"
    if code == 16:
        return msg + "identifier expected"
    if code == 17:
        return msg + "';' expected"
    if code == 18:
        return msg + "'=' expected"
    if code == 19:
        return msg + "identifier, if, or while expected"
    if code == 99:
        return msg + "syntax error"
    return msg + "syntax error"

# get error code from parse state
def getErrorCode(state):
    # EOF expected
    if state == 6:
        return 6
    # identifier expected
    if state in [1, 5, 24, 28]:
        return 7
    # special word missing
    if state in [0, 2, 4, 9, 13, 37, 45, 46, 50]:
        return 8
    # symbol missing
    if state in [3, 7, 11, 23, 30, 40]:
        return 9
    # data type expected
    if state in [29]:
        return 10
    # identifier or literal value expected
    if state in [25, 26, 27, 33, 55, 56, 57, 58, 59, 60, 61, 62]:
        return 11
    return 99

# lexeme to token conversion map
lookupToken = {
    "$"         : Token.EOF,
    "+"         : Token.ADD,
    "-"         : Token.SUBTRACT,
    "*"         : Token.MULTIPLY,
    "/"         : Token.DIVIDE,
    "("         : Token.OPEN_PAR,
    ")"         : Token.CLOSE_PAR
}

# a tree-like data structure
class Tree:

    TAB = "   "

    def __init__(self):
        self.data     = None
        self.children = []

    def add(self, child):
        self.children.append(child)

    def print(self, tab = ""):
        if self.data != None:
            print(tab + self.data)
            tab += self.TAB
            for child in self.children:
                if isinstance(child, Tree):
                    child.print(tab)
                else:
                    print(tab + child)

# reads the next char from input and returns its class
def getChar(input):
    if len(input) == 0:
        return (None, CharClass.EOF)
    c = input[0].lower()
    if c.isalpha():
        return (c, CharClass.LETTER)
    if c.isdigit():
        return (c, CharClass.DIGIT)
    if c == '"':
        return (c, CharClass.QUOTE)
    if c in ['+', '-', '*', '/']:
        return (c, CharClass.OPERATOR)
    if c in ['.', ';']:
        return (c, CharClass.PUNCTUATOR)
    if c in [' ', '\n', '\t']:
        return (c, CharClass.BLANK)
    if c in ['(', ')']:
        return (c, CharClass.DELIMITER)
    return (c, CharClass.OTHER)

# calls getChar and addChar until it returns a non-blank
def getNonBlank(input):
    ignore = ""
    while True:
        c, charClass = getChar(input)
        if charClass == CharClass.BLANK:
            input, ignore = addChar(input, ignore)
        else:
            return input

# adds the next char from input to lexeme, advancing the input by one char
def addChar(input, lexeme):
    if len(input) > 0:
        lexeme += input[0]
        input = input[1:]
    return (input, lexeme)

# returns the next (lexeme, token) pair or ("", EOF) if EOF is reached
def lex(input):
    input = getNonBlank(input)

    c, charClass = getChar(input)
    lexeme = ""

    # checks EOF
    if charClass == CharClass.EOF:
        return (input, lexeme, Token.EOF)

    # reads an identifier
    if charClass == CharClass.LETTER:
        input, lexeme = addChar(input, lexeme)
        while True:
            c, charClass = getChar(input)
            if charClass == CharClass.LETTER or charClass == CharClass.DIGIT:
                input, lexeme = addChar(input, lexeme)
            else:
                return (input, lexeme, Token.IDENTIFIER)

    # reads digits
    if charClass == CharClass.DIGIT:
        input, lexeme = addChar(input, lexeme)
        while True:
            c, charClass = getChar(input)
            if charClass == CharClass.DIGIT:
                input, lexeme = addChar(input, lexeme)
            else:
                return (input, lexeme, Token.LITERAL)

    # reads operator
    if charClass == CharClass.OPERATOR:
        input, lexeme = addChar(input, lexeme)
        if lexeme in lookupToken:
            return (input, lexeme, lookupToken[lexeme])

    # reads parenthesis
    if charClass == CharClass.DELIMITER and (c == '(' or c == ')'):
        input, lexeme = addChar(input, lexeme)
        return (input, lexeme, lookupToken[lexeme])

    # anything else, raises an error
    raise Exception(errorMessage(3))

# reads the given input and returns the grammar as a list of productions
def loadGrammar(input):
    grammar = []
    for line in input:
        grammar.append(line.strip())
    return grammar

# returns the LHS (left hand side) of a given production
def getLHS(production):
    return production.split("->")[0].strip()

# returns the RHS (right hand side) of a given production
def getRHS(production):
    return production.split("->")[1].strip().split(" ")

# prints the productions of a given grammar, one per line
def printGrammar(grammar):
    i = 0
    for production in grammar:
        print(str(i) + ". " + getLHS(production), end = " -> ")
        print(getRHS(production))
        i += 1

# reads the given input containing an SLR parsing table and returns the "actions" and "gotos" as dictionaries
def loadTable(input):
    actions = {}
    gotos = {}
    header = input.readline().strip().split(",")
    end = header.index("$")
    tokens = []
    for field in header[1:end]:
        tokens.append(int(field))
    tokens.append(int(Token.EOF)) # '$' is replaced by token -1
    variables = header[end + 1:]
    for line in input:
        row = line.strip().split(",")
        state = int(row[0])
        for i in range(len(tokens)):
            token = tokens[i]
            key = (state, token)
            value = row[i + 1]
            if len(value) == 0:
                value = None
            actions[key] = value
        for i in range(len(variables)):
            variable = variables[i]
            key = (state, variable)
            value = row[i + len(tokens) + 1]
            if len(value) == 0:
                value = None
            gotos[key] = value
    return (actions, gotos)

# prints the given actions, one per line
def printActions(actions):
    for key in actions:
        print(key, end = " -> ")
        print(actions[key])

# prints the given gotos, one per line


def printGotos(gotos):
    for key in gotos:
        print(key, end = " -> ")
        print(gotos[key])

# given an input (source program), a grammar, actions, and gotos, returns the
# corresponding parse tree or raise an exception if syntax errors were found
def parse(input, grammar, actions, gotos):

    # TODOd: create a stack of trees
    trees = []

    # TODOd: initialize the stack of (state, symbol) pairs
    stack = []
    stack.append(0)

    # initialize lexeme and token variables
    lexeme = ""
    token  = None

    # main parser loop
    while True:

        # get lex info ONLY if token is None
        if token is None:
            input, lexeme, token = lex(input)

        # TODOd: get current state
        state = stack[-1]

        # print debugging info
        if DEBUG:
            print("stack:",                    end = " ")
            print(stack,                       end = " ")
            print("(\"" + lexeme + "\", ",     end = " ")
            print(token,                       end = ",")
            print(" " + str(int(token)) + ")", end = " ")

        # TODOd: get action
        action = actions[(state, token)]

        if DEBUG:
            print("action:",                   end = " ")
            print(action)

        # if action is undefined, raise an approriate error
        if action is None:
            errorCode = getErrorCode(state)
            raise Exception(errorMessage(errorCode))

        # TODO: implement the shift operation
        if action[0] == 's':

            # TODOd: update the stack
            stack.append(int(token))
            state = int(action[1:])
            stack.append(state)

            # TODOd: create a new tree, set data to token, and push it onto the list of trees
            tree = Tree()
            tree.data = lexeme
            trees.append(tree)

            # set token to None to acknowledge reading the input
            token = None

        # TODO: implement the reduce operation
        elif action[0] == 'r':

            # TODOd: get production to use
            production = grammar[int(action[1:])]
            lhs = getLHS(production)
            rhs = getRHS(production)

            # TODOd: update the stack
            for i in range(len(rhs) * 2):
                stack.pop()
            state = stack[-1]
            stack.append(lhs)
            stack.append(int(gotos[(state, lhs)]))

            # TODOd: create a new tree and set data to lhs
            newTree = Tree()
            newTree.data = lhs

            # TODOd: get "len(rhs)" trees from the right of the list of trees and add each of them as child of the new tree you created, preserving the left-right order
            for tree in trees[-len(rhs):]:
                newTree.add(tree)

            # TODOd: remove "len(rhs)" trees from the right of the list of trees
            trees = trees[:-len(rhs)]

            # TODOd: append the new tree to the list of trees
            trees.append(newTree)

        # TODO: implement the "accept" operation
        else:

            # TODOd: set lhs as the start symbol; assume that the lhs of the 1st production has the start symbol
            production = grammar[0]
            lhs = getLHS(production)

            # TODOd: reduce all trees to the start symbol
            newTree = Tree()
            newTree.data = lhs
            for tree in trees:
                newTree.add(tree)

            # TODOd: return the new tree
            return newTre


# main
if __name__ == "__main__":

    # checks if source file was passed and if it exists
    try:
        if len(sys.argv) != 2:
            raise ValueError(errorMessage(1))
        sourceFile = None
        try:
            sourceFile = open(sys.argv[1], "rt")
        except:
            pass
        if not sourceFile:
            raise IOError(errorMessage(2))
        input = sourceFile.read()
        sourceFile.close()
    except Exception as ex:
        print(ex)
        sys.exit(1)

    # main loop
    # output = []
    # while True:
    #     input, lexeme, token = lex(input)
    #     if token == Token.EOF:
    #         break
    #     output.append((lexeme, token))

    # prints the output
    # for (lexeme, token) in output:
    #     print(lexeme, token)

    # load grammar
    try:
        grammarFile = None
        try:
            grammarFile = open("../grammar.txt", "rt")
        except:
            pass
        if not grammarFile:
            raise IOError(errorMessage(4))
        grammar = loadGrammar(grammarFile)
        grammarFile.close()
        printGrammar(grammar)
    except Exception as ex:
        print(ex)
        sys.exit(1)

    # load SLR table
    try:
        slrTableFile = None
        try:
            slrTableFile = open("../slr_table.csv", "rt")
        except:
            pass
        if not slrTableFile:
            raise IOError(errorMessage(5))
        actions, gotos = loadTable(slrTableFile)
        slrTableFile.close()
        # printActions(actions)
        # printGotos(gotos)
    except Exception as ex:
        print(ex)
        sys.exit(1)

    # parse the code
    # try:
    #     tree = parse(input, grammar, actions, gotos)
    #     print("Input is syntactically correct!")
    #     print("Parse Tree:")
    #     tree.print("")
    # except Exception as ex:
    #     print(ex)
    #     sys.exit(1)
