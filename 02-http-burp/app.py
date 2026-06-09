"""
02-http-burp: HTTPと Burp Suite マスターしよう
クリハクティブの一巻で終わるウェブハッキングバイブル - Ch02 マッピング

このアプリの目的:
- HTTP リクエスト/応答の全ての要素(メソッド、ヘッダ、パラメータ、クッキー、バディ)を直接目で確認
- Burp Suiteで"全てのトラフィックを拡え取って見る"経験を初めからする
- 本で強調されている"ユーザー入力値がどうやってサーバまで渡るか"を体感

実行:
    python app.py
    ブラウザ: http://127.0.0.1:5001
"""

from flask import Flask, request, render_template_string, make_response, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "for-study-only-not-real-secret"

# 簡単なインメモリDB (実習用)
def get_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            name TEXT,
            phone TEXT,
            email TEXT,
            is_admin INTEGER DEFAULT 0
        )
    """)
    # 本初期で出てくる"铁水/水美"例を為にしたデータ
    c.executemany("""
        INSERT INTO users (username, name, phone, email, is_admin) VALUES (?, ?, ?, ?, ?)
    """, [
        ("chulsu", "铁水", "010-1234-5678", "chulsu@example.com", 0),
        ("sumi", "水美", "010-9876-5432", "sumi@example.com", 0),
        ("admin", "管理者", "010-0000-0000", "admin@secret.local", 1),
    ])
    return conn

DB = get_db()

# HTML テンプレート (簡単にインライン)
INDEX_HTML = """
<!doctype html>
<html>
<head><meta charset="utf-8"><title>ウェブハッキング実習 ターゲット #1 - HTTP マスター</title></head>
<body style="font-family: sans-serif; max-width: 800px; margin: 40px auto;">
    <h1>🔥 ウェブ ハッキング 実習 ターゲット #1</h1>
    <p><strong>目標:</strong> Burp Suiteでこのサイトの全てのリクエストを拡え取って分析せよ。</p>
    <hr>

    <h2>1. 簡単な GET リクエスト 実習 (会員情報参照)</h2>
    <p>本 Ch01で出てきたその例をそのまま再現した。</p>
    <form action="/profile" method="GET">
        <label>参照するユーザー名: 
            <input type="text" name="user" value="chulsu" size="20">
        </label>
        <button type="submit">会員情報を見る</button>
    </form>
    <p style="color:#666; font-size:0.9em;">
        ヒント: ?user=chulsu の代わりに ?user=sumi または ?user=admin で変更してリクエストを送ってみよう (パラメータ変更の味見本)
    </p>

    <h2>2. POST リクエスト 実習 (ログイン)</h2>
    <form action="/login" method="POST">
        <label>アイディ: <input type="text" name="username" value="chulsu"></label><br><br>
        <label>パスワード: <input type="password" name="password" value="test123"></label><br><br>
        <button type="submit">ログイン</button>
    </form>
    <p style="color:#666; font-size:0.9em;">実際はパスワード検証がほぼない (実習用)。 Burpでリクエストバディを必ず確認しろ。</p>

    <h2>3. クッキー/セッション 実習</h2>
    <p><a href="/myinfo">私の情報を見る (ログイン必須)</a></p>
    <p style="color:#666;">ログイン後に発行されるセッションクッキーを Burpで確認し、別の人のクッキーで変更してみよう。</p>

    <hr>
    <h3>Burp 使用 チェックリスト (このアプリで必ずやってみよう)</h3>
    <ol>
        <li>Burp 実行 → Proxy → Intercept is on</li>
        <li>ブラウザプロクシを 127.0.0.1:8080 に設定 (FoxyProxy 推奨)</li>
        <li>上のフォームを送信しながら Burpでリクエストを <strong>拡え取って</strong> ヘッダ/パラメータ/バディを全部見る</li>
        <li>Forward して実際に送信</li>
        <li>History タブで過去リクエストを確認 + Repeaterで再送信練習</li>
    </ol>

    <p><strong>今すぐ試してみよう:</strong> /profile?user=chulsu リクエストを Burp Repeaterで送って、user パラメータを sumi に変更して Forward してみよう。</p>
</body>
</html>
"""

PROFILE_HTML = """
<!doctype html>
<html>
<head><meta charset="utf-8"><title>会員情報</title></head>
<body style="font-family: sans-serif; max-width: 600px; margin: 40px auto;">
    <h1>会員情報参照結果</h1>
    {% if user %}
        <table border="1" cellpadding="8">
            <tr><th>アイディ</th><td>{{ user.username }}</td></tr>
            <tr><th>名前</th><td>{{ user.name }}</td></tr>
            <tr><th>電話番号</th><td>{{ user.phone }}</td></tr>
            <tr><th>メール</th><td>{{ user.email }}</td></tr>
            <tr><th>管理者？</th><td>{{ 'はい' if user.is_admin else 'いいえ' }}</td></tr>
        </table>
        <p style="color:red; font-weight:bold;">
            ⚠️ 注意: ここでは ?user パラメータをあらゆる検証なしでそのまま使用している。<br>
            これが正に "パラメータ変更脆弱点"の開始点だ。
        </p>
    {% else %}
        <p>ユーザーが見つかりません。</p>
    {% endif %}
    <p><a href="/">← メインに戻る</a></p>
</body>
</html>
"""

LOGIN_HTML = """
<!doctype html>
<html>
<head><meta charset="utf-8"><title>ログイン結果</title></head>
<body style="font-family: sans-serif; max-width: 600px; margin: 40px auto;">
    <h1>ログイン結果</h1>
    <p>{{ message }}</p>
    {% if success %}
        <p><a href="/myinfo">私の情報ページへ移動</a></p>
    {% endif %}
    <p><a href="/">← メインに戻る</a></p>
</body>
</html>
"""

MYINFO_HTML = """
<!doctype html>
<html>
<head><meta charset="utf-8"><title>私の情報 (ログイン必須)</title></head>
<body style="font-family: sans-serif; max-width: 600px; margin: 40px auto;">
    <h1>私の情報 (セッション基盤)</h1>
    {% if user %}
        <p>こんにちは、<strong>{{ user.name }}</strong>さん！</p>
        <p>電話番号: {{ user.phone }}</p>
        <p>メール: {{ user.email }}</p>
        {% if user.is_admin %}
            <p style="color:red;">🎉 管理者権限確認されました。 (後で admin 機能実習に使用)</p>
        {% endif %}
    {% else %}
        <p style="color:red;">ログインが必要です。 /login へ行ってログインしてください。</p>
    {% endif %}
    <p><a href="/">← メインに戻る</a></p>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(INDEX_HTML)


@app.route("/profile")
def profile():
    """
    [脆弱点ポイント - 本 Ch01 例と同一]
    ?user= 値を受けてあらゆる検証/権限チェックなしで直接DB取得。
    これがパラメータ変更 + 後で IDORへ発展する基礎。
    """
    username = request.args.get("user", "chulsu")
    
    # ★★★ ここが脆弱！ (意図的)
    # 実際は現在ログイン中のユーザーがこの user を見る権限があるかを確認しなければならない。
    c = DB.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))  # ← それでも ? placeholder は使ったが、ロジック自体が問題
    row = c.fetchone()
    
    if row:
        user = dict(row)
    else:
        user = None
    
    return render_template_string(PROFILE_HTML, user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return redirect(url_for("index"))
    
    # POST データ受け取り (Burpで body を必ず確認しろ)
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    
    # 実習用: パスワードはほぼ無視 (chulsu / test123 だけ通過させる)
    # 後で SQLi チャプターで本物の脆弱ログインにアップグレード予定
    success = False
    message = "ログイン失敗"
    
    if username == "chulsu" and password == "test123":
        success = True
        message = "铁水 ログイン成功！ セッションが発行されました。"
        resp = make_response(render_template_string(LOGIN_HTML, message=message, success=success))
        resp.set_cookie("session_user", "chulsu", httponly=True)  # httponlyだがまだ secureではない
        return resp
    elif username == "admin" and password == "test123":  # adminも同一 pw で便宜
        success = True
        message = "管理者 ログイン成功！"
        resp = make_response(render_template_string(LOGIN_HTML, message=message, success=success))
        resp.set_cookie("session_user", "admin", httponly=True)
        return resp
    else:
        return render_template_string(LOGIN_HTML, message="アイディまたはパスワードが間違っています。", success=False)


@app.route("/myinfo")
def myinfo():
    """
    クッキー(セッション)基盤認証例。
    Burpでクッキーを拡え取って別のユーザーで偽装する練習をさせる。
    """
    session_user = request.cookies.get("session_user")
    if not session_user:
        return render_template_string(MYINFO_HTML, user=None)
    
    c = DB.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (session_user,))
    row = c.fetchone()
    user = dict(row) if row else None
    return render_template_string(MYINFO_HTML, user=user)


@app.route("/debug/request")
def debug_request():
    """
    Burp なしでも現在リクエストの全ての情報を見れるように作ったデバッグページ。
    (学習用) 実際攻撃するときは Burp History + Repeater を使うのが正式。
    """
    info = {
        "method": request.method,
        "path": request.path,
        "args": dict(request.args),
        "form": dict(request.form),
        "headers": dict(request.headers),
        "cookies": dict(request.cookies),
        "remote_addr": request.remote_addr,
    }
    return f"<pre>{info}</pre>"


if __name__ == "__main__":
    print("=" * 60)
    print("02-http-burp 実習アプリ開始")
    print("接続: http://127.0.0.1:5001")
    print("Burp Proxyを 127.0.0.1:8080 に設定して使いましょう！")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5001, debug=True)
