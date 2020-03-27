"""
CS3210 Programming Assignment 1
Authors:
    Thyago Mota (original author of code below)
    Robb Hill (edited code below)
"""


# CS 3210 - Principles of Programming Languages - Spring 2020
# A bottom-up parser for an expression

from enum import IntEnum
import sys

# enables parser's debugging
DEBUG = True

# all char classes
class CharClass(IntEnum):
    EOF        = 0
    LETTER     = 1
    DIGIT      = 2
    OPERATOR   = 3
    PUNCTUATOR = 4
    QUOTE      = 5
    BLANK      = 6
    DELIMITER  = 7
    RELATION   = 8
    ASSIGNMENT = 9
    OTHER      = 10

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
    "": Token.EOF,
    "int": Token.INT_TYPE,
    "main": Token.MAIN,
    "(": Token.OPEN_PAR,
    ")": Token.CLOSE_PAR,
    "[": Token.OPEN_BRACKET,
    "]": Token.CLOSE_BRACKET,
    "{": Token.OPEN_CURLY,
    "}": Token.CLOSE_CURLY,
    # ".": Token.PERIOD,
    # "'": Token.QUOTE,
    ",": Token.COMMA,
    "=": Token.ASSIGNMENT,
    ";": Token.SEMICOLON,
    "if": Token.IF,
    "else": Token.ELSE,
    "while": Token.WHILE,
    "||": Token.OR,
    "&&": Token.AND,
    "==": Token.EQUALITY,
    "!=": Token.INEQUALITY,
    "<": Token.LESS,
    "<=": Token.LESS_EQUAL,
    ">": Token.GREATER,
    ">=": Token.GREATER_EQUAL,
    "+": Token.ADD,
    "-": Token.SUBTRACT,
    "*": Token.MULTIPLY,
    "/": Token.DIVIDE,
    "bool": Token.BOOL_TYPE,
    "float": Token.FLOAT_TYPE,
    "char": Token.CHAR_TYPE,
    "true": Token.TRUE,
    "false": Token.FALSE
}



# reads the next char from input and returns its class
def getChar(inpt):
    if len(inpt) == 0:
        return (None, CharClass.EOF)
    c = inpt[0].lower()
    if c.isalpha():
        return (c, CharClass.LETTER)
    if c.isdigit():
        return (c, CharClass.DIGIT)
    # if c == '"':
    #     return (c, CharClass.QUOTE)
    if c in ['+', '-', '*', '/']:
        return (c, CharClass.OPERATOR)
    if c in ['.', ';', ',', "'"]:
        return (c, CharClass.PUNCTUATOR)
    if c in [' ', '\n', '\t']:
        return (c, CharClass.BLANK)
    if c in ['(', ')', '[', ']', '{', '}']:
        return (c, CharClass.DELIMITER)
    if c in ['<', '<=', '>', '>=', '==', '!=']:
        return (c, CharClass.RELATION)
    if c in ['=']:
        return (c, CharClass.ASSIGNMENT)
    return (c, CharClass.OTHER)

# calls getChar and addChar until it returns a non-blank
def getNonBlank(inpt):
    ignore = ""
    while True:
        c, charClass = getChar(inpt)
        if charClass == CharClass.BLANK:
            inpt, ignore = addChar(inpt, ignore)
        else:
            return inpt

# adds the next char from input to lexeme, advancing the input by one char
def addChar(inpt, lexeme):
    if len(inpt) > 0:
        lexeme += inpt[0]
        inpt = inpt[1:]
    return (inpt, lexeme)

# returns the next (lexeme, token) pair or ("", EOF) if EOF is reached
def lex(inpt):
    inpt = getNonBlank(inpt)

    c, charClass = getChar(inpt)
    lexeme = ""

    # checks EOF
    if charClass == CharClass.EOF:
        return (inpt, lexeme, Token.EOF)

    # reads an identifier
    if charClass == CharClass.LETTER:
        inpt, lexeme = addChar(inpt, lexeme)
        while True:
            c, charClass = getChar(inpt)
            if charClass == CharClass.LETTER or charClass == CharClass.DIGIT:
                inpt, lexeme = addChar(inpt, lexeme)
            else:
                if lexeme in lookupToken:
                    return (inpt, lexeme, lookupToken[lexeme])
                return (inpt, lexeme, Token.IDENTIFIER)

    # reads digits
    if charClass == CharClass.DIGIT:
        inpt, lexeme = addChar(inpt, lexeme)
        while True:
            c, charClass = getChar(inpt)
            if charClass == CharClass.DIGIT:
                inpt, lexeme = addChar(inpt, lexeme)
            elif charClass == CharClass.PUNCTUATOR:
                inpt, lexeme = addChar(inpt, lexeme)
            else:
                return (inpt, lexeme, Token.INT_LITERAL)

    # reads operator
    if charClass == CharClass.OPERATOR:
        inpt, lexeme = addChar(inpt, lexeme)
        if lexeme in lookupToken:
            return (inpt, lexeme, lookupToken[lexeme])

    # reads parenthesis, brackets, braces and excellent novels
    if charClass == CharClass.DELIMITER and (c == '(' or c == ')' or c == '{' or c == '}' or c == '[' or c == ']'):
        inpt, lexeme = addChar(inpt, lexeme)
        return (inpt, lexeme, lookupToken[lexeme])


    # reads punctuators
    if charClass == CharClass.PUNCTUATOR and (c == ',' or c == ';' or c == '.'):
        inpt, lexeme = addChar(inpt, lexeme)
        return (inpt, lexeme, lookupToken[lexeme])

    if c == "'":
        inpt = getNonBlank(inpt)
        inpt, lexeme = addChar(inpt, lexeme)
        trim = getNonBlank(inpt) # cuts off trailing ' to prevent double evaluation
        return (trim, lexeme, Token.CHAR_LITERAL)


    if charClass == CharClass.ASSIGNMENT:
        inpt, lexeme = addChar(inpt, lexeme)
        if lexeme in lookupToken:
            return (inpt, lexeme, lookupToken[lexeme])

    if charClass == CharClass.RELATION:
        inpt, lexeme = addChar(inpt, lexeme)
        if lexeme in lookupToken:
            return (inpt, lexeme, lookupToken[lexeme])

    # anything else, raises an error
    print(inpt, charClass, c)
    raise Exception(errorMessage(3))

# reads the given input and returns the grammar as a list of productions
def loadGrammar(inpt):
    grammar = []
    for line in inpt:
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
def loadTable(inpt):
    actions = {}
    gotos = {}
    header = inpt.readline().strip().split(",")
    end = header.index('$')
    tokens = []
    for field in header[1:end]:
        tokens.append(int(field))
    tokens.append(int(Token.EOF)) # '$' is replaced by token -1
    variables = header[end + 1:]
    for line in inpt:
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

# given an inpt (source program), a grammar, actions, and gotos, returns the corresponding parse tree or raise an exception if syntax errors were found
def parse(inpt, grammar, actions, gotos):

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
            inpt, lexeme, token = lex(inpt)

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

        # if action is undefined, raise an appropriate error
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

            # set token to None to acknowledge reading the inpt
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
            return newTree

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
        inpt = sourceFile.read()
        sourceFile.close()
    except Exception as ex:
        print(ex)
        sys.exit(1)

    # main loop
    output = []
    while True:
        inpt, lexeme, token = lex(inpt)
        if token == Token.EOF:
            break
        output.append((lexeme, token))

    # prints the output
    for (lexeme, token) in output:
        print(lexeme, token)

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
        printActions(actions)
        printGotos(gotos)
    except Exception as ex:
        print(ex)
        sys.exit(1)

    # parse the code
    try:
        tree = parse(inpt, grammar, actions, gotos)
        print("inpt is syntactically correct!")
        print("Parse Tree:")
        tree.print("")
    except Exception as ex:
        print(ex)
        sys.exit(1)