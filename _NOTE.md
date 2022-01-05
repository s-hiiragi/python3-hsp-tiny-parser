# 開発メモ

## TODO

- [x] 簡単な式を追加する (`Any + Any`)
- [x] トークンに行番号と桁番号を持たせる
- [x] 行コメント、末尾コメント、範囲コメントを実装する
- [x] ラベル定義構文を実装する
- [x] ラベルリテラルを実装する
- [ ] デバッグログを吐かせる
- [ ] 式ノードの構造を簡素化する
- [ ] 配列定義構文を実装する
- [ ] 割り込み文を実装する (button)
- [ ] 実数リテラルを実装する
- [ ] 演算子を充実させる
- [ ] マルチステートメントを実装する
- [ ] if文を実装する
- [ ] プリプロセッサを実装する
- [x] inputs/にFizzBuzzを追加する
- [ ] inputs/に`Brainf*ck`インタプリタを追加する
- [ ] while,do-until,forを構文として実装する

## 設計方針

- 普通書かないような記述パターンには対応しない
  - 参考: if文について(後述)

### 制限事項

- 文は改行で終わる必要がある (EOFの前に改行が必要)
  - Tokenに文末を判定するメソッドがあると良いかも (NEWLINE, COLON, EOFのいずれかならTrue)

## 疑問

- Exprノードがあった方がよい？
- 三項以上の演算子ノードは二項演算子ノードに変えた方がよい？

## メモ

### ラベルリテラルについて

- ラベルを字句解析でトークンにするのは難しい
  - ラベル定義文のラベルについては、'*'の直前のトークンが改行であればラベルと判別できる
  - ローカルラベル(`*@`等)については、他の文法と衝突しないので判別できる
  - 式中のラベル(参照)については、二項乗算演算子と区別するのが難しい

### if文について

if文の構文解析がどうなっているのか実機にて調べた
結果として、普通書かないような記述パターンがいくつか見つかった

TODO ドキュメントも確認したい

調査環境

- [Try HSP3Dish](http://peppermint.jp/products/hsp/try.html)

if文

```hsp
    if 0 : mes "a"
    ; ==> (空)

    ; then節(`:`スタイル)は複数記述できる
    if 0 : mes "a" : mes "b"
    ; ==> (空)

    ; then節(`:`スタイル)は途中で改行できない
    if 0
    : mes "a"
    ; ==> a

    if 0 :
    mes "a"
    ; ==> a

    ; then節を次の行に書くことはできない
    ; (then節(`:`スタイル)はマルチステートメントとは異なる)
    if 0
    mes "a"
    ; ==> a

    ; then節は`{}`で囲むことができる
    if 0 { mes "a" : mes "b" }
    ; ==> (空)

    ; then節(`{}`スタイル)は改行できる
    if 0 {
        mes "a"
    }
    ; ==> (空)

    ;then節の`{`はif文と同じ行に書く必要がある
    if 0
    { mes "a" }
    ; ==> error 16 : if命令以外で{〜}が使われています (N行目)

    ; 中括弧の後のマルチステートメントはthen節にならない
    if 0 { mes "a" } : mes "b"
    ; ==> b

    if 0 {
        mes "a"
    } : mes "b"
    ; ==> b
```

if-else文

```hsp
    if 0 : mes "a" : else : mes "b"
    ; ==> b

    if 0 { mes "a" } else { mes "b" }
    ; ==> b

    if 0 {
        mes "a"
    } else {
        mes "b"
    }
    ; ==> b

    ; then節(`:`スタイル)は途中で改行できない

    if 0 : mes "a"
    : else : mes "b"
    ; ==> error 14 : elseの前にifが見当たりません (N行目)

    if 0 : mes "a" :
    else : mes "b"
    ; ==> error 14 : elseの前にifが見当たりません (N行目)

    ; then節(`:`スタイル)に対するelse節は次の行に書けない

    if 0 : mes "a"
    else : mes "b"
    ; ==> error 14 : elseの前にifが見当たりません (N行目)

    if 0 : mes "a"
    else { mes "b" }
    ; ==> error 14 : elseの前にifが見当たりません (N行目)

    ; then節(`{}`スタイル)に対するelse節は次の行に書ける

    if 0 { mes "a" }
    else : mes "b"
    ; ==> b

    if 0 { mes "a" }
    else { mes "b" }
    ; ==> b

    ; ただし、ifとelseの間に空行を入れるとエラーとなる

    if 0 { mes "a" }

    else : mes "b"
    ; ==> error 14 : elseの前にifが見当たりません (N行目)

    if 0 { mes "ar" }

    else { mes "br" }
    ; ==> error 14 : elseの前にifが見当たりません (N行目)
```

if-else if文

- else ifはないので、elseとifを組み合わせて使う

```hsp
    if 0 : mes "a" : else : if 1 : mes "b"
    ; ==> b

    if 0 { mes "a" } else : if 1 { mes "b" }
    ; ==> b
```

以下、コンパイラのバグと思われる入力パターン

```hsp
    ; then節に`:`スタイルと`{}`スタイルを混在できてしまう

    if 0 : mes "a" {
        mes "b"
    } else {
        mes "c"
    }
    ; ==> c

    if 1 : mes "a" : mes "a2" { mes "a3" } else : mes "b"
    ; ==> a
    ;     a2
    ;     a3

    ; else節も同様

    if 0 : mes "a" : else : mes "b" { mes "c" }
    ; ==> b
    ;     c

    ; if文のthen節は省略できてしまう

    if 0
    mes "a"
    ; ==> a

    if 0 : else : mes "b"
    ; ==> b

    ; elseに引数を指定できてしまう (コンパイルが通ってしまう)
    ; 引数を指定すると、else節が実行されない

    if 0 : mes "a" : else "b" : mes "c"
    ; ==> (空)

    ; elseを複数書けてしまう (コンパイルが通ってしまう)
    ; 偶数番目のelseは実行されない

    if 0 {
        mes "a"
    } else {
        mes "1"
    } else {
        mes "2"
    } else {
        mes "3"
    } else {
        mes "4"
    } else {
        mes "5"
    }
    ; ==> 1
    ;     3
    ;     5
```
