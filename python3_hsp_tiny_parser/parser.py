from typing import Optional
from enum import Enum, auto
from collections import namedtuple
from .tokenizer import Tokenizer, Token


class Node():

    class NodeType(Enum):
        STMTS = auto()
        EMPTY_STMT = auto()
        ASSIGN_STMT = auto()
        CALL_STMT = auto()
        ARGS = auto()
        EXPR = auto()
        ADD_EXPR = auto()
        ATOM = auto()

    TAG_TO_STR = {
        NodeType.STMTS : 'Stmts',
        NodeType.EMPTY_STMT : 'Empty',
        NodeType.ASSIGN_STMT : '=',
        NodeType.CALL_STMT : 'Call',
        NodeType.ARGS : 'Args',
        NodeType.EXPR : 'Expr',
        NodeType.ADD_EXPR : '+',
        NodeType.ATOM : 'Atom'
    }

    def __init__(self, tag, *tokens):
        self.tag = tag
        self.tokens = tokens

    def tag_str(self):
        if self.tag not in self.TAG_TO_STR:
            raise RuntimeError(f'__repr__: unknown tag "{self.tag}"')

        return self.TAG_TO_STR[self.tag]

    @classmethod
    def Stmts(cls, *tokens):
        return Node(cls.NodeType.STMTS, *tokens)

    @classmethod
    def EmptyStmt(cls):
        return Node(cls.NodeType.EMPTY_STMT, [])

    @classmethod
    def AssignStmt(cls, *tokens):
        return Node(cls.NodeType.ASSIGN_STMT, *tokens)

    @classmethod
    def CallStmt(cls, *tokens):
        return Node(cls.NodeType.CALL_STMT, *tokens)

    @classmethod
    def Args(cls, *tokens):
        return Node(cls.NodeType.ARGS, *tokens)

    @classmethod
    def Expr(cls, *tokens):
        return Node(cls.NodeType.EXPR, *tokens)

    @classmethod
    def AddExpr(cls, *tokens):
        return Node(cls.NodeType.ADD_EXPR, *tokens)

    @classmethod
    def Atom(cls, *tokens):
        return Node(cls.NodeType.ATOM, *tokens)

    def __repr__(self):
        def join(tokens):
            return " ".join(map(str, tokens))

        if len(self.tokens) == 0:
            return self.tag_str()
        elif self.tag == self.NodeType.ATOM:
            return f'{self.tokens[0]}'
        else:
            return f'({self.tag_str()} {join(self.tokens)})'


def print_node(node, nestlevel=0):
    indent = '  ' * nestlevel

    if node.tag == Node.NodeType.ATOM:
        node_str = f'Atom:{node}'
    else:
        node_str = node.tag_str()

    print(f'{indent}{node_str}')

    if node.tag != Node.NodeType.ATOM:
        for t in node.tokens:
            print_node(t, nestlevel+1)


MatchResult = namedtuple('MatchResult', ['value', 'num_consumed'])


class ParseError(Exception):
    pass


class Parser():

    def __init__(self):
        pass

    def _read_srcfile(self, srcfile):
        with open(srcfile, encoding='CP932') as f:
            return f.read()

    def parse(self, srcfile: str) -> Node:
        src = self._read_srcfile(srcfile)

        tokens = Tokenizer().tokenize(src)
        print('parse: tokens')
        print(tokens)
        print([format(t, '({src}:{row}:{column})') for t in tokens])

        ast = self.parse_tokens(tokens)
        print('parse: ast')
        print(ast)
        print_node(ast)

        return ast

    def parse_tokens(self, tokens: list[Token]) -> Node:
        stmts = []

        i = 0
        while tokens[i].tag != Token.TokenType.EOF:

            if m := self._match_stmt(tokens[i:]):
                stmts.append(m.value)
                i += m.num_consumed
            else:
                raise ParseError(f'''parse_tokens: unexpected token {format(tokens[i], '"{src}" (row:{row} column:{column})')}''')

        return Node.Stmts(*stmts)

    def _match_stmt(self, tokens) -> Optional[MatchResult]:
        methods = [
            self._match_empty_stmt,
            self._match_assign_stmt,
            self._match_call_stmt,
        ]

        for match in methods:
            if m := match(tokens):
                if tokens[m.num_consumed].tag == Token.TokenType.NEWLINE:
                    return MatchResult(m.value, m.num_consumed + 1)

    def _match_empty_stmt(self, tokens) -> Optional[MatchResult]:
        return MatchResult(Node.EmptyStmt(), 0)

    def _match_assign_stmt(self, tokens) -> Optional[MatchResult]:
        if len(tokens) < 3:
            return
        if tokens[0].tag != Token.TokenType.ID:
            return
        if tokens[1].src != '=':
            return

        if m := self._match_expr(tokens[2:]):
            pass
        else:
            return

        target = Node.Atom(tokens[0])
        node = Node.AssignStmt(target, m.value)
        return MatchResult(node, 2 + m.num_consumed)

    def _match_call_stmt(self, tokens) -> Optional[MatchResult]:
        if len(tokens) < 1:
            return
        if tokens[0].tag != Token.TokenType.ID:
            return

        args = []
        i = 1
        n = len(tokens)
        while i < n:
            if tokens[i].tag == Token.TokenType.NEWLINE:
                break
            if tokens[i].tag == Token.EOF:
                break

            if m := self._match_expr(tokens[i:]):
                args.append(m.value)
                i += m.num_consumed
            else:
                # TODO 任意の引数は省略できる
                return

            # TODO 引数の間にはカンマが必要

        func = Node.Atom(tokens[0])
        node = Node.CallStmt(func, Node.Args(*args))
        return MatchResult(node, i)

    def _match_expr(self, tokens) -> Optional[MatchResult]:
        if len(tokens) < 1:
            return

        if m := self._match_addexpr(tokens):
            return m

    def _match_addexpr(self, tokens) -> Optional[MatchResult]:
        if len(tokens) < 1:
            return

        operands = []

        if m := self._match_atom(tokens):
            operands.append(m.value)
        else:
            return

        i = 1
        n = len(tokens)
        while i < n:
            if tokens[i].src == '+' or tokens[i].src == '-':
                i += 1
            else:
                if len(operands) == 1:
                    # +/-演算子が1つも無い場合はマッチ失敗とする
                    return
                else:
                    break

            if m := self._match_atom(tokens[i:]):
                operands.append(m.value)
                i += 1
            else:
                return

        node = Node.AddExpr(*operands)
        return MatchResult(node, i)

    def _match_atom(self, tokens) -> Optional[MatchResult]:
        if len(tokens) < 1:
            return

        atom_tags = [
            Token.TokenType.ID,
            Token.TokenType.INT,
            Token.TokenType.STR
        ]

        if tokens[0].tag in atom_tags:
            node = Node.Atom(tokens[0])
            return MatchResult(node, 1)
