import pytest
from python3_hsp_tiny_parser.tokenizer import TokenPosition, Token, TokenizeError, Tokenizer
from python3_hsp_tiny_parser.parser import Node, ParseError, Parser


Id = Token.Id
Int = Token.Int
Str = Token.Str

Stmts = Node.Stmts
LabelStmt = Node.LabelStmt
AssignStmt = Node.AssignStmt
CallStmt = Node.CallStmt
Args = Node.Args
Expr = Node.Expr
AddExpr = Node.AddExpr
SubExpr = Node.SubExpr
Atom = Node.Atom

POS = TokenPosition(1, 1)


@pytest.fixture
def parser():
    return Parser()


def test_init(parser):
    pass


def test_atom_ctor():
    atom = Atom(value=1)
    assert atom.tag == Node.NodeType.ATOM
    assert len(atom.child_nodes) == 0
    assert atom.value == 1


def test_stmts_ctor_with_0args():
    stmts = Stmts()
    assert stmts.tag == Node.NodeType.STMTS
    assert len(stmts.child_nodes) == 0
    assert stmts.value is None


def test_stmts_ctor_with_1arg():
    stmts = Stmts(Atom(value=1))
    assert stmts.tag == Node.NodeType.STMTS
    assert len(stmts.child_nodes) == 1
    assert stmts.value is None
    assert stmts.child_nodes[0] == Atom(value=1)


def test_stmts_ctor_with_2args():
    stmts = Stmts(Atom(value=1), Atom(value=2))
    assert stmts.tag == Node.NodeType.STMTS
    assert len(stmts.child_nodes) == 2
    assert stmts.value is None
    assert stmts.child_nodes[0] == Atom(value=1)
    assert stmts.child_nodes[1] == Atom(value=2)


@pytest.mark.parametrize('src', ['', '\n'])
def test_empty_src(parser, src):
    ast = parser.parse_str(src)
    assert ast == Stmts()


def test_label_stmt(parser):
    ast = parser.parse_str('*main\n')
    assert ast == Stmts(LabelStmt(Atom(value=Id(POS, 'main'))))


def test_assign_stmt(parser):
    ast = parser.parse_str('x=1\n')
    assert ast == Stmts(AssignStmt(Atom(value=Id(POS, 'x')), Atom(value=Int(POS, '1'))))


def test_call_stmt(parser):
    ast = parser.parse_str('x 1\n')
    assert ast == Stmts(CallStmt(Atom(value=Id(POS, 'x')), Args(Atom(value=Int(POS, '1')))))
