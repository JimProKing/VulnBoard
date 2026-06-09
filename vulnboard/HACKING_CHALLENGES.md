# VulnBoard ハッキング チャレンジ ガイド
## クリハクティブ ウェブ ハッキング バイブル 実習 マッピング (特に SQL Injection 中心)

このサイトは **意図的に脆弱** に作られています。  
目標は"攻撃成功"ではなく、 **各技法の動作原理を体で理解** することです。

**強力推奨**: 全ての攻撃は Burp Suite を通してやりましょう。 Repeater を愛用しよう。

---

## 事前準備
1. `python app.py` 実行 (ポート 5002)
2. Burp プロクシ ON (127.0.0.1:8080)
3. ブラウザプロクシ設定
4. 基本アカウントでログインテスト: `chulsu` / `test123`
5. DB 初期化が必要なら `/reset` ページ訪問 (いつでも可能)

---

## SQL Injection チャレンジ (本 Ch04 核心)

### Level 1: ログイン建回 ( 最も基本 )
** 目標 **: SQL Injection で `admin` アカウントにログインする (パスワードを知らないで)

**推奨進入点**: `/login`

**試してみるペイロード例** (直接変形してみよう):
- `admin' -- `
- `' OR '1'='1' -- `
- `admin' OR 1=1 -- `

**成功基準**: "管理者" 権限でログインされ、上部ナビに管理者メニューが見えるか `/admin` アクセスが容易になる。

**学習ポイント**:
- 認証クエリがどう書かれているか逆推理
- コメント(`-- `, `#`, `/* */`)の役割
- Burp Repeater で数十回繰り返し攻撃する習慣

---

### Level 2: 投稿板検索 SQLi (UNION 基盤)
**進入点**: `/board?q=...` または `/search?q=...`

**目標**:
1. エラーを発生させてカラム数を把握 (ORDER BY 10 など)
2. UNION SELECT で `users` テーブルの username, password, is_admin などを抽出
3. `secrets` テーブルの flag まで抽出

**有用な技法**:
- `' UNION SELECT 1,2,3,4,5,6 -- `
- カラム数合わせ ( エラーメッセージが親切に教えてくれる )
- `secrets` テーブルは id, owner, secret, flag カラムを持つ

**成功基準**: secrets テーブルの FLAG{...} を最低 2個以上画面で確認

---

### Level 3: 投稿文 ID 基盤 SQLi (一番現実的なパターン)
**進入点**: `/post/1` , `/post/2` など

**目標**:
- `/post/1' ` でエラー発生
- UNION または エラー基盤で別のテーブルデータダンプ
- 特に `secrets` テーブルの flag 抽出

**高度**:
- `1 AND 1=2 UNION SELECT ...` (Blind 準備)
- カラムタイプ合わせ (テキスト vs 数値)

---

### Level 4: Boolean Blind SQLi
**進入点**: 検索や post ID

**目標**: 真/偽によってページ応答(結果数、エラー有無、内容長など)が違うのを利用して一文字ずつデータ抽出。

**例ロジック**:
- `1' AND SUBSTR((SELECT password FROM users WHERE username='admin'),1,1)='a' -- `
- 結果が"ある"または"ない"、またはエラー vs 正常で区別

**ツール実習**: Burp Intruder で自動化または簡単な Python スクリプト作成推奨。

---

### Level 5: Time-based Blind SQLi
このアプリでは DB レベル SLEEP が限定的なので、アプリ レベルで条件付き遅延を一部サポートしています。

**実習方法**:
- 検索や ID で特定条件が真の時に応答が遅くなるクエリを書く
- (実際は Python time.sleep を条件で呼び出している)

**成功基準**: `secrets` テーブルの `FLAG{TIME_BASED_SQLi_MASTER}` 取得

**参照**: 実際 MySQL/PostgreSQL では `SLEEP()`, `pg_sleep()` などを使う。本で詳細に扱っています。

---

### Level 6: Second-order SQLi (高度)
コメントに悪意のあるペイロードを保存し、後でその内容が別のクエリで使われた時に発動。

現在のコメントは主に Stored XSS 用だが、拡張して second-order を体験できる地点を追加可能。

---

## 他のチャプターマッピングチャレンジ

### Broken Access Control / IDOR (Ch11, Ch10)
- `/profile/admin` または `/profile/sumi` 直接アクセス
- ログインなし、または一般アカウントで管理者権限獲得
- `/admin` ページ建回 ( セッション変更、SQLi で is_admin=1 作り、 param tamper )

### Stored XSS + セッション脱取 (Ch06)
- `/post/1` などにコメントで `<script>alert(document.cookie)</script>` または更進んでクッキーを攻撃者サーバへ送信するペイロード挿入
- (このサイトはまだ外部サーバがないので、 console.log や alert で先に確認)

### File Upload (Ch09)
- `/upload` でウェブシェル(簡単な PHP や JSP ではなく、このアプリは Python なので .py ファイルをアップロードして直接呼び出してみよう)
- ファイル名に `../../../` を入れて上位ディレクトリアクセス試行
- アップロード後 `/uploads/ファイル名` で直接アクセス

### OS Command Injection (Ch05)
- `/tools/ping` ページ
- `127.0.0.1 & whoami` または `127.0.0.1 | dir C:\` など
- もっと進んで `& type vulnboard.db` で DB ファイル内容読み取り試行 (可能か？)

---

## 最終ボス チャレンジ (総合)

1. SQLi だけで `admin` アカウント脱取 + secrets の全フラグ取得
2. Stored XSS で管理者セッションクッキー脱取 シミュレーション
3. File upload で悪意のファイルアップロード後実行
4. `/admin` 完全アクセス + ユーザー削除機能悪用
5. (ボーナス) Command Injection でサーバ情報最大限収集

---

## 学習チップ (本の精神に合わせて)

- **無条件 Burp Repeater 使用** しよう。ブラウザ地址栏だけでは絶対にならない。
- エラーメッセージを無視しない。カラム数、テーブル構造を教えてくれる最高の友達です。
- `UNION SELECT` の時はカラム個数とタイプを合わせる練習を大量にしよう。
- Blind は面白くないが、 **一文字ずつ抽出するロジック** を自分でコードで書いてみるのが本物の実力です。
- "このクエリが実際にどう書かれているか？" を常に想像しながら攻撃しよう。 (本が強調している部分)
- 成功した攻撃はスクリーンショット + Repeater ヒストリを保存しておこう。

---

## 次の段階提案

VulnBoard で十分 SQLi を掘り就ったら:
- 本の残りのチャプター (XSS、CSRF、ファイルアップロード詳細など) マッピングしてより複雑な脆弱点を追加したり
- 公式例 (insecure_board JSP) を Docker で起動して比較してみよう
- 実際 CTF 問顂や PortSwigger Web Security Academy へ移行

今は **この一つのサイトを徹底的に破壊** するに集中しよう。

迷ったら任意の時点で「Level 3で UNION カラム数が合わない」または 「admin でログインしたのに /admin が開かない」 と言ってくれ。一緒に解決しよう。

幸運を祈っています。 (そして面白くやってください！)
