# 烫 VulnBoard

**「公撃知らなければ防御が見える」 — クリハクティブの一巻で終わるウェブハッキングバイブル実践練習場**

> 本 900ページ読むの面白くないという人へ。  
> **じゃぁ直接破壊してみろ。**  
> Burpをオンにして、SQL Injectionでadminになるその味を味い触え。

VulnBoardは**意図的に脆弱な**一つのウェブサイト + 基礎例題で構成された**安全なハッキング遊び場**だ。

---

## 🚀 30秒で始める

```bash
git clone https://github.com/JimProKing/VulnBoard.git
cd VulnBoard/webhacking-bible-lab/vulnboard
pip install -r ../../requirements.txt
python app.py
```

ブラウザで http://127.0.0.1:5002 開いて  
**Burp Suite**をケンにしよう (これが本当の主人公)

基本アカウント:
- `admin` / `admin123!@#`
- `chulsu` / `test123`

---

## 🎮 主要チャレンジ (HACKING_CHALLENGES.md 必読)

- **Level 1**: ログイン SQLiで admin 脱取 (`admin' -- ` の味)
- **Level 2**: 検索で UNIONで secrets テーブルを就る
- **Level 3~5**: 投稿文 ID、Blind、Time-based SQLi
- **ボーナス**: Stored XSS、IDOR、Broken Access Control、ファイルアップロード、Command Injection

secrets テーブルに **FLAG** が隠されている。全部食べれば勝利。

---

## 🛠️ 入っているもの

| フォルダ          | 内容                              | 本マッピング |
|---------------|-----------------------------------|------------------|
| `vulnboard/`  | メイン脆弱ブログ ( 強推 ) | Ch04~Ch11       |
| `01-basics/`  | なぜウェブが攻撃味フードか？ | Ch01            |
| `02-http-burp`| HTTP + Burp 完全正制             | Ch02            |

全ての脆弱点コードに `# VULNERABLE:` コメントを付けてある。  
直接ソースを見ながら「あ、この一行のせいで...」と実感しよう。

---

## ⚠️ 真剣の重要注意事項

- これは **学習用**だ。実際サービスにこんなのを放ったら本当に監狶が行く。
- `/reset` を押すとDBが美しくなる。実験して壊してもOK。
- Burp Repeaterを神のように社にしろ。

---

## 💡 学習チップ (クリハクティブスタイル)

1. 無条件 Burpで全てのリクエストを拡え取れ
2. エラーメッセージを無視するな (あれが你の友達)
3. 「このクエリが実際にどうなってるか？」を想像しながら攻撃
4. 成功したペイロードは Repeaterに保存
5. 迷ったら「Level 2でカラム数が合わない」と言えば手伝う

---

## 📦 実行方法 (Windows)

```powershell
# 1. クローン
git clone https://github.com/JimProKing/VulnBoard.git
cd VulnBoard\webhacking-bible-lab

# 2. 依存関係
pip install -r requirements.txt

# 3. VulnBoard実行 (メイン)
cd vulnboard
python app.py
```

---

## 🎉 このプロジェクトが生まれた理由

使用者が「本読むのは面白くない、ウェブサイトを直接作ってハッキングしながら学びたい」と言ったから誕生したプロジェクト。

小さな例題を数多く作るのではなく、**一つの本格的な脆弱サイト**を作って、実際のハッキング感覚を養うことを目的にした。

公式本例 (Tomcat+JSP)は重いから、こちらは Flask + SQLiteで軽く、Windowsでもすぐに動かせるようにした。

---

**さぁ、adminアカウントを就れ。**

成功したら「Level 1 クリア」と言ってくれ。
次のレベルへ導いてあげる。

ハッキング楽しくな！ 🔥

*(このプロジェクトはクリハクティブバイブル学習用で作られ、実際攻撃実練は絶対禁止)*

---

Made with ❤️ (and a lot of `admin' -- `) by Grok for you.
