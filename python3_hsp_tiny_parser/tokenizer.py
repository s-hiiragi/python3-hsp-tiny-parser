import re
from enum import Enum, auto
from collections import namedtuple


TokenPosition = namedtuple('TokenPosition', ['row', 'column'])


class Token():

    class TokenType(Enum):
        ID = auto()
        INT = auto()
        STR = auto()
        SIGN = auto()
        # TODO セミコロンと改行は同じ扱いで良い？
        NEWLINE = auto()
        EOF = auto()

    TAG_TO_STR = {
        TokenType.ID : 'ID',
        TokenType.INT : 'INT',
        TokenType.STR : 'STR',
        TokenType.SIGN : 'SIGN',
        TokenType.NEWLINE : '\\n',
        TokenType.EOF : 'EOF'
    }

    def __init__(self, tag, pos: TokenPosition, src: str):
        self.tag = tag
        self.pos = pos
        self.src = src

    def tag_str(self) -> str:
        if self.tag not in self.TAG_TO_STR:
            raise RuntimeError(f'Unknown tag {self.tag}')
        return self.TAG_TO_STR[self.tag]

    @classmethod
    def Id(cls, pos: TokenPosition, src: str):
        return Token(cls.TokenType.ID, pos, src)

    @classmethod
    def Int(cls, pos: TokenPosition, src: str):
        return Token(cls.TokenType.INT, pos, src)

    @classmethod
    def Str(cls, pos: TokenPosition, src: str):
        return Token(cls.TokenType.STR, pos, src)

    @classmethod
    def Sign(cls, pos: TokenPosition, src: str):
        return Token(cls.TokenType.SIGN, pos, src)

    @classmethod
    def Newline(cls, pos: TokenPosition):
        return Token(cls.TokenType.NEWLINE, pos, '<LF>')

    @classmethod
    def EOF(cls, pos: TokenPosition):
        return Token(cls.TokenType.EOF, pos, '<EOF>')

    def __repr__(self) -> str:
        if self.tag == self.TokenType.ID:
            return f'ID[{self.src}]'
        elif self.tag == self.TokenType.INT:
            return f'{self.src}'
        elif self.tag == self.TokenType.STR:
            return f'"{self.src}"'
        elif self.tag == self.TokenType.SIGN:
            return f'SIGN[{self.src}]'
        elif self.tag == self.TokenType.NEWLINE:
            return '\\n'
        elif self.tag == self.TokenType.EOF:
            return 'EOF'
        else:
            raise RuntimeError(f'__repr__: Unknown tag "{self.tag}"')

    def __format__(self, format_spec):
        if format_spec:
            return format_spec.format(tag=self.tag, pos=self.pos, row=self.pos.row, column=self.pos.column, src=self.src)
        else:
            return repr(self)


class TokenizeError(Exception):
    def __init__(self, message: str, pos: TokenPosition):
        self.args = f'{message} (at row:{pos.row} column:{pos.column})',


class Tokenizer():

    ONE_CHARACTER_SIGNS = list('=+-')

    def __init__(self):
        pass

    def tokenize(self, src):
        tokens = []

        i = 0
        n = len(src)
        row = 1
        column_origin = 0

        def get_pos():
            return TokenPosition(row, i - column_origin + 1)

        while i < n:
            pos = get_pos()
            c = src[i]
            if c in [' ', '\t']:
                pass
            elif c == '\n':
                # 改行が連続する場合は1つまで追加する
                if len(tokens) == 0 or tokens[-1].tag != Token.TokenType.NEWLINE:
                    tokens.append(Token.Newline(pos))

                row += 1
                column_origin = i + 1
            elif c == '\r':
                # Skip CR
                i += 1
                if src[i] != '\n':
                    raise TokenizeError('missing LF', pos)

                # 改行が連続する場合は1つまで追加する
                if len(tokens) == 0 or tokens[-1].tag != Token.TokenType.NEWLINE:
                    tokens.append(Token.Newline(pos))

                row += 1
                column_origin = i + 1
            elif c == '"':
                i += 1

                s = None
                j = i
                while j < n:
                    c = src[j]
                    if c == '"':
                        s = src[i:j]
                        break
                    if c == '\\':
                        # Skip next char
                        j += 1
                    j += 1
                if s is None:
                    raise TokenizeError('tokenize: missing closing \'"\'', pos)
                i = j
                tokens.append(Token.Str(pos, s))
            elif m := re.match(r'[1-9]\d*', src[i:]):
                s = m.group(0)
                tokens.append(Token.Int(pos, s))
                i += len(s) - 1
            elif m := re.match(r'[_a-zA-Z]\w*', src[i:]):
                s = m.group(0)
                tokens.append(Token.Id(pos, s))
                i += len(s) - 1
            elif c in self.ONE_CHARACTER_SIGNS:
                tokens.append(Token.Sign(pos, c))
            else:
                raise TokenizeError(f'tokenize: unknown char \'{c}\'', pos)

            i += 1

        tokens.append(Token.EOF(get_pos()))

        return tokens
