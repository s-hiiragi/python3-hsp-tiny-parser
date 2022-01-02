from typing import Optional, Union
from enum import Enum, auto
from pathlib import Path
from collections import namedtuple
from .tokenizer import Tokenizer, Token


class Node():

    class NodeType(Enum):
        STMTS = auto()
        EMPTY_STMT = auto()
        LABEL_STMT = auto()
        ASSIGN_STMT = auto()
        CALL_STMT = auto()
        ARGS = auto()
        EXPR = auto()
        ADD_EXPR = auto()
        SUB_EXPR = auto()
        ATOM = auto()

    TAG_TO_STR = {
        NodeType.STMTS : 'Stmts',
        NodeType.EMPTY_STMT : 'Empty',
        NodeType.LABEL_STMT : 'Label',
        NodeType.ASSIGN_STMT : '=',
        NodeType.CALL_STMT : 'Call',
        NodeType.ARGS : 'Args',
        NodeType.EXPR : 'Expr',
        NodeType.ADD_EXPR : '+',
        NodeType.SUB_EXPR : '-',
        NodeType.ATOM : 'Atom'
    }

    def __init__(self, tag, *child_nodes, value=None):
        self.tag = tag
        self.child_nodes = child_nodes
        self.value = value

    def tag_str(self):
        if self.tag not in self.TAG_TO_STR:
            raise RuntimeError(f'__repr__: unknown tag "{self.tag}"')

        return self.TAG_TO_STR[self.tag]

    @classmethod
    def Stmts(cls, *child_nodes):
        return Node(cls.NodeType.STMTS, *child_nodes)

    @classmethod
    def EmptyStmt(cls):
        return Node(cls.NodeType.EMPTY_STMT)

    @classmethod
    def LabelStmt(cls, *child_nodes):
        return Node(cls.NodeType.LABEL_STMT, *child_nodes)

    @classmethod
    def AssignStmt(cls, *child_nodes):
        return Node(cls.NodeType.ASSIGN_STMT, *child_nodes)

    @classmethod
    def CallStmt(cls, *child_nodes):
        return Node(cls.NodeType.CALL_STMT, *child_nodes)

    @classmethod
    def Args(cls, *child_nodes):
        return Node(cls.NodeType.ARGS, *child_nodes)

    @classmethod
    def Expr(cls, *child_nodes):
        return Node(cls.NodeType.EXPR, *child_nodes)

    @classmethod
    def AddExpr(cls, *child_nodes):
        return Node(cls.NodeType.ADD_EXPR, *child_nodes)

    @classmethod
    def SubExpr(cls, *child_nodes):
        return Node(cls.NodeType.SUB_EXPR, *child_nodes)

    @classmethod
    def Atom(cls, *, value):
        return Node(cls.NodeType.ATOM, value=value)

    def __repr__(self):
        def join(child_nodes):
            return " ".join(map(str, child_nodes))

        if len(self.child_nodes) == 0:
            return self.tag_str()
        elif self.tag == self.NodeType.ATOM:
            return f'{self.value}'
        else:
            return f'({self.tag_str()} {join(self.child_nodes)})'


def print_node(node, nestlevel=0):
    indent = '  ' * nestlevel

    if node.tag == Node.NodeType.ATOM:
        print(f'{indent}Atom:{node.value}')
    elif len(node.child_nodes) == 0:
        print(f'{indent}{node.tag_str()} []')
    else:
        print(f'{indent}{node.tag_str()}')
        for t in node.child_nodes:
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

    def parse_file(self, srcfile: Union[Path, str]) -> Node:
        src = self._read_srcfile(srcfile)
        return self.parse_str(src)

    def parse_str(self, src: str) -> Node:
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
                if m.value.tag != Node.NodeType.EMPTY_STMT:  # Skip EmptyStmt
                    stmts.append(m.value)
                i += m.num_consumed
            else:
                raise ParseError(f'''parse_tokens: unexpected token {format(tokens[i], '"{src}" (row:{row} column:{column})')}''')

        return Node.Stmts(*stmts)

    def _match_stmt(self, tokens: list[Token]) -> Optional[MatchResult]:
        methods = [
            self._match_empty_stmt,
            self._match_label_stmt,
            self._match_assign_stmt,
            self._match_call_stmt,
        ]

        for match in methods:
            if m := match(tokens):
                if tokens[m.num_consumed].tag == Token.TokenType.NEWLINE:  # Consume NEWLINE
                    return MatchResult(m.value, m.num_consumed + 1)

    def _match_empty_stmt(self, tokens: list[Token]) -> Optional[MatchResult]:
        if len(tokens) < 1:
            return
        if tokens[0].tag != Token.TokenType.NEWLINE:
            return
        return MatchResult(Node.EmptyStmt(), 0)

    def _match_label_stmt(self, tokens: list[Token]) -> Optional[MatchResult]:
        if len(tokens) < 2:
            return
        if tokens[0].src != '*':
            return
        if tokens[1].tag != Token.TokenType.ID:
            return
        return MatchResult(Node.LabelStmt(Node.Atom(value=tokens[1])), 2)

    def _match_assign_stmt(self, tokens: list[Token]) -> Optional[MatchResult]:
        if len(tokens) < 3:
            return
        if tokens[0].tag != Token.TokenType.ID:
            return
        if tokens[1].src != '=':
            return

        if m := self._match_expr(tokens[2:]):
            pass
        elif m := self._match_atom(tokens[2:]):
            pass
        else:
            return

        target = Node.Atom(value=tokens[0])
        node = Node.AssignStmt(target, m.value)
        return MatchResult(node, 2 + m.num_consumed)

    def _match_call_stmt(self, tokens: list[Token]) -> Optional[MatchResult]:
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

        func = Node.Atom(value=tokens[0])
        node = Node.CallStmt(func, Node.Args(*args))
        return MatchResult(node, i)

    def _match_expr(self, tokens: list[Token]) -> Optional[MatchResult]:
        if len(tokens) < 1:
            return

        if m := self._match_addexpr(tokens):
            return m

    def _match_addexpr(self, tokens: list[Token]) -> Optional[MatchResult]:
        if len(tokens) < 1:
            return

        operands = []

        if m := self._match_atom(tokens):
            operands.append(m.value)
        else:
            return

        i = 1
        n = len(tokens)
        op = None
        while i < n:
            if tokens[i].src == '+' or tokens[i].src == '-':
                op = tokens[i].src
                i += 1
            else:
                if len(operands) == 1 and operands[0].tag == Node.NodeType.ATOM:
                    # +/-演算子が1つも無い場合はマッチ失敗とする
                    return
                else:
                    break

            if m := self._match_atom(tokens[i:]):
                operands.append(m.value)
                # TODO operandsのオペランド2つを演算子ノードに包んでoperandsに入れる
                if op == '+':
                    node = Node.AddExpr(*operands)
                else:
                    node = Node.SubExpr(*operands)
                operands = [node]
                i += 1
            else:
                print(2)
                return

        #node = Node.AddExpr(*operands)
        node = operands[0]
        return MatchResult(node, i)

    def _match_atom(self, tokens: list[Token]) -> Optional[MatchResult]:
        if len(tokens) < 1:
            return

        atom_tags = [
            Token.TokenType.ID,
            Token.TokenType.INT,
            Token.TokenType.STR
        ]

        if tokens[0].tag in atom_tags:
            node = Node.Atom(value=tokens[0])
            return MatchResult(node, 1)
