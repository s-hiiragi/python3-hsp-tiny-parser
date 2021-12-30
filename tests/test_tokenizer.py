import pytest
from python3_hsp_tiny_parser.tokenizer import TokenPosition, Token, TokenizeError, Tokenizer


POS = TokenPosition(1, 1)
EOF = Token.EOF(POS)


@pytest.fixture
def tok():
    return Tokenizer()


def test_init(tok):
    pass


def test_empty(tok):
    tokens = tok.tokenize('')
    assert len(tokens) == 1
    assert tokens[0] == EOF


@pytest.mark.parametrize('src', ['x', '_', '_x'])
def test_valid_id(tok, src):
    tokens = tok.tokenize(src)
    assert len(tokens) == 2
    assert tokens[0] == Token.Id(POS, src)
    assert tokens[1] == EOF


@pytest.mark.parametrize('src', ['0', '123'])
def test_valid_int(tok, src):
    tokens = tok.tokenize(src)
    assert len(tokens) == 2
    assert tokens[0] == Token.Int(POS, src)
    assert tokens[1] == EOF


@pytest.mark.parametrize('src', ['01'])
def test_invalid_int(tok, src):
    with pytest.raises(TokenizeError) as e:
        __ = tok.tokenize(src)


@pytest.mark.parametrize('src', ['""', '"str"'])
def test_valid_str(tok, src):
    tokens = tok.tokenize(src)
    assert len(tokens) == 2
    assert tokens[0] == Token.Str(POS, src[1:-1])
    assert tokens[1] == EOF


@pytest.mark.parametrize("src", ['"', '"str'])
def test_invalid_str(tok, src):
    with pytest.raises(TokenizeError) as e:
        __ = tok.tokenize(src)


@pytest.mark.parametrize("src", ['\n', '\r\n'])
def test_valid_newline(tok, src):
    tokens = tok.tokenize(src)
    assert len(tokens) == 2
    assert tokens[0] == Token.Newline(POS)
    assert tokens[1] == EOF


@pytest.mark.parametrize("src", ['\r'])
def test_invalid_newline(tok, src):
    with pytest.raises(TokenizeError) as e:
        __ = tok.tokenize(src)


@pytest.mark.parametrize("src", ['\n\n', '\r\n\r\n', '\n\r\n', '\r\n\n'])
def test_dedupe_newline(tok, src):
    tokens = tok.tokenize(src)
    assert len(tokens) == 2
    assert tokens[0] == Token.Newline(POS)
    assert tokens[1] == EOF


@pytest.mark.parametrize("src", [';comment', '//comment'])
def test_valid_line_comment(tok, src):
    tokens = tok.tokenize(src)
    assert len(tokens) == 1
    assert tokens[0] == EOF


@pytest.mark.parametrize("src", ['/**/', '/* comment */', '/* \n */'])
def test_valid_block_comment(tok, src):
    tokens = tok.tokenize(src)
    assert len(tokens) == 1
    assert tokens[0] == EOF


@pytest.mark.parametrize("src", ['/*'])
def test_invalid_block_comment(tok, src):
    with pytest.raises(TokenizeError) as e:
        __ = tok.tokenize(src)
