"""
01-basics: ウェブハッキングとは何か？ (本 Chapter 01 マッピング)

このアプリの目的:
- "なぜウェブが攻撃味フードか？" をコードと一緒に体感
- ユーザー入力値検証未少が全ての脆弱点の開始点であることを示す
- 本 Ch01で出てきた"铁水 → 水美 情報脱取"例を最小コードで再現

理論は本を読んでもらうとして、ここでは"直接触ってみること"に集中。
"""

from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        CREATE TABLE memos (
            id INTEGER PRIMARY KEY,
            owner TEXT,
            content TEXT,
            is_secret INTEGER DEFAULT 0
        )
    """)
    c.executemany("INSERT INTO memos (owner, content, is_secret) VALUES (?, ?, ?)", [
        ("chulsu", "今日の午食はキムチチゲ", 0),
        ("sumi", "铁水に高白しようか迷ってる...", 1),   # 非密メモ
        ("admin", "フラグ{webhacking_is_fun_with_input_validation}", 1),
    ])
    return conn

DB = get_db()

INDEX = """
<h1>01-basics: なぜウェブが攻撃味フードか？</h1>
<p>このサイトは <strong>とても簡単なメモ帳</strong>です。</p>
<ul>
  <li>ログインなしで誰でもメモを"参照"できる</li>
  <li>owner パラメータで他人のメモを見れる (検証なし)</li>
</ul>

<h2>他人のメモを見る (パラメータ操作テスト)</h2>
<form action="/memo" method="GET">
    owner: <input name="owner" value="chulsu">
    <button>見る</button>
</form>

<p>試してみる値: chulsu, sumi, admin</p>
<p><a href="/memo?owner=sumi">直接リンクで sumi を見る</a></p>

<hr>
<p style="color:#c00;">
    この例の核心: サーバが owner 値を"ただ信じて"使用する。<br>
    実際サービスでは"現在ログイン中のユーザーがこの owner のメモを見る権限があるか？"を必ず確認しなければならない。
</p>
"""

MEMO = """
<h1>メモ参照結果</h1>
{% if memo %}
    <p><strong>作成者:</strong> {{ memo.owner }}</p>
    <p><strong>内容:</strong> {{ memo.content }}</p>
    {% if memo.is_secret %}
        <p style="color:red;">(非密メモ)</p>
    {% endif %}
{% else %}
    <p>メモがありません。</p>
{% endif %}

<p><a href="/">もう一度試す</a></p>
"""


@app.route("/")
def index():
    return render_template_string(INDEX)


@app.route("/memo")
def view_memo():
    """
    [意図的脆弱点]
    owner パラメータを受けてあらゆる権限検査なしで直接取得。
    これが"入力値検証未少"の最も単純な形態。
    """
    owner = request.args.get("owner", "chulsu")
    
    # ★ 脆弱なコードの核心
    c = DB.cursor()
    c.execute("SELECT * FROM memos WHERE owner = ?", (owner,))
    row = c.fetchone()
    
    if row:
        return render_template_string(MEMO, memo=dict(row))
    return render_template_string(MEMO, memo=None)


if __name__ == "__main__":
    print("01-basics アプリ開始: http://127.0.0.1:5000")
    app.run(port=5000, debug=True)
