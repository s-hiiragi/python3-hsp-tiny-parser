# HSPの文法


## ミニマルな言語機能を作る

実装するもの
- プリプロセッサ
  - `#include`
  - `#const`
  - `#define` (非マクロ関数)
  - `#module`, `#global` (モジュール変数なし)
  - `#deffunc`, `#defcfunc`
- コメント
  - [ ] 行コメント (空行または行末)
  - [ ] 範囲コメント
- 文
  - [ ] 複合文
  - [ ] マルチステートメント
  - [x] 代入文
  - [ ] 累算代入文
  - [ ] 配列変数への連続代入文
  - [x] 命令文
    - [ ] 実引数の省略
  - [ ] ラベル定義文
    - http://www.onionsoft.net/hsp/v35/doclib/hspprog.htm#FUNC
- [x] 式
  - [ ] 関数呼出し式
  - [x] 識別子
  - [x] リテラル (10進整数、文字列)
  - [ ] ラベルリテラル (`*ID`)
  - [ ] 配列変数の参照 (書式ver3)
  - [ ] 優先順位変更の括弧
  - [x] 演算子
    - http://www.onionsoft.net/hsp/v35/doclib/hspprog.htm#EXPRESSION
    - [ ] 乗算演算子、除算演算子
    - [x] 加算演算子、減算演算子
    - [ ] 比較演算子(`==,=,!=,!,<=,>=,<,>`)
- 開発支援
  - [x] エラー時のトークン位置表示

実装しないもの
- プリプロセッサ
- DLL呼出し
- COMのサポート
- ローカルラベル定義文 (`*@`)
- ローカルラベル参照 (`*@back`/`*@b`, `*@forward`/`*@f`)
- 一部のリテラル
  - 16進整数、2進整数、10進実数、文字コード
    - http://www.onionsoft.net/hsp/v35/doclib/hspprog.htm#EXPRESSION
  - 複数行文字列
    - http://www.onionsoft.net/hsp/v35/doclib/hspprog.htm#STRING
- 配列変数 (書式ver2)
- 論理演算子 (`&,|,^`)


## ミニマルな命令セットを作る

何の用途を想定するか？
- ツール
- ゲーム

システム変数
- cnt, stat
数学定数
- M_PI
オブジェクト制御命令
- button, input
プログラム制御命令
- await, wait
- break, continue, foreach, loop, repeat
- else, end, if, return, stop
- gosub, goto, onclick, onkey, onexit
メモリ管理命令
- dim, sdim
基本入出力制御命令
- getkey, randomize, stick
- rnd()
基本入出力関数

## マニュアルに記載のない言語機能

### インクリメント/デクリメント文

`x+`, `x++`
`x-`, `x--`

http://www.onionsoft.net/hsp/v35/doclib/hspprog.htm#VAR
- 3.8に記載があった。

### 累算代入文

`x @= y`
`@ : +,-,*,/,\,&,|,^,!,<<,>>,<=,>=`

http://www.onionsoft.net/hsp/v35/doclib/hspprog.htm#VAR
- 3.8に記載があった。

`x@y`は`x@=y`と同じ (罠)
- 例外がある
  - `x<=y`は`x = x <= y`と同じ (罠)
    - `x@y`の方が`x@=y`より優先して解釈されるのだと思われる

`x==y`が代入文`x=y`と同じ (罠)
- 式中の`==`(比較)と文中の`==`(代入)は意味が違う

`x===y`はエラー


## 挙動の確認

### 未定義変数の参照

未定義変数を参照してもエラーにならず、暗黙のうちに定義された変数への参照となる (罠)

```hsp
mes undefined_variable  #==> 0と表示される
```

### if文と`:`の挙動

`:`は1行に複数の命令を記述するためのデリミタ (この機能をマルチステートメントという)
http://www.onionsoft.net/hsp/v35/doclib/hspprog.htm#MULTI_STATEMENT

if文の場合、`:`は単なるマルチステートメントの意味ではない。
`:`以降はthen節(条件が真のときに実行される文)となる。
then節はif文の次の行に書くことはできず、`:`でマルチステートメントにするか、`{}`で囲む必要がある。

```hsp
a = 1
if a == 2 : mes "a"  ;==> (表示なし)

if a == 2
mes "a"  ;==> a
```


## HSP4は必要か？

https://twitter.com/bd_gfngfn/status/459680118449766401
> HSP，いつかもう少し文法の整ったHSP4がリリースされないかなって思ったりしてる

Cons
- 現状の文法でもそこまで不満はない


## HSPの強みは？

https://twitter.com/YSRKEN/status/805235262519316480
> HSPが強いのは、たとえクソみたいな文法だとしても、
> ・GUIをポンポン出せて
> ・exeファイルもすぐ作れる
> ・スクリプト言語
> が他にないということではないでしょうか。後、DLLを一応叩けるので
> ・気合と根性さえあれば何でもできる
> ・グルー言語
> だというのも大きそうですわ

https://twitter.com/bolero_MURAKAMI/status/805232885506547712
> 本当にクソでしかない環境は（デファクトでもなければ）流行ることもないので、すごい人がやってるってことは HSP にもそれなりに光るものがあるってことですよ。

HSP3Dishは強みを捨ててしまっている
- 配置オブジェクトが制限された
  - http://www.onionsoft.net/hsp/v35/doclib/hsp3dish_prog.htm#BUTTON
    > 現在サポートされている配置オブジェクトは、button命令によるボタンのみとなっています。
  - ゲーム向けであれば配置オブジェクトは使わないだろうから、問題なし？
  - ツールを作りづらいと思う
