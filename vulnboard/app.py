#!/usr/bin/env python3
"""
VulnBoard - クリハクティブウェブハッキングバイブル実習用脆弱ウェブサイト
主要フォーカス: SQL Injection (Ch04) + 本の後半攻撃技法

このアプリは意図的に複数の脆弱点を含んでいます。
実際サービスに絶対使用しないでください。学習専用です。

実行:
    python app.py

接続: http://127.0.0.1:5002

特徴:
- Flask + SQLite (軽量、Windowsですぐ実行)
- 複数の SQLi 進入点 (error, union, boolean blind, time-based, login, search, IDOR-style)
- Stored XSS (コメント)
- Broken Access Control / IDOR
- 簡単なファイルアップロード (後で拡張)
- 管理者ページ (脆弱な権限チェック)
- 全ての主要リクエストは Burpで観察/攻撃しよう！

コードに # VULNERABLE: コメントで脆弱な部分を明示。
"""

import os
import sqlite3
import time
import random
from datetime import datetime
from flask import (
    Flask, request, render_template, redirect, url_for,
    session, flash, send_from_directory, make_response
)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "vulnboard-insecure-for-study-only-2026"
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DB_PATH = os.path.join(os.path.dirname(__file__), 'vulnboard.db')

# ============================================================
# Database initialization (rich data for SQLi practice)
# ============================================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Users table - classic target for SQLi
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            nickname TEXT,
            email TEXT,
            is_admin INTEGER DEFAULT 0,
            created_at TEXT
        )
    ''')

    # Posts (board)
    c.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            content TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Comments (stored XSS + SQLi practice)
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            user_id INTEGER,
            content TEXT,
            created_at TEXT,
            FOREIGN KEY(post_id) REFERENCES posts(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Secrets table - for UNION / blind dumping practice
    c.execute('''
        CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY,
            owner TEXT,
            secret TEXT,
            flag TEXT
        )
    ''')

    # Files (for upload vuln later)
    c.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename TEXT,
            original_name TEXT,
            uploaded_at TEXT
        )
    ''')

    # Seed data (only if empty)
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        now = datetime.now().isoformat()
        users = [
            ("admin", "admin123!@#", "管理者", "admin@vulnboard.local", 1, now),
            ("chulsu", "test123", "铁水", "chulsu@example.com", 0, now),
            ("sumi", "sumi2025", "水美", "sumi@secret.local", 0, now),
            ("guest", "guest", "手伝い", "guest@vulnboard.local", 0, now),
        ]
        c.executemany(
            "INSERT INTO users (username, password, nickname, email, is_admin, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            users
        )

        # Posts
        posts = [
            (1, "公告事項: VulnBoard オープン", "みなさん歓迎します。このサイトはウェブハッキング実習用で作られました。複数の脆弱点が隠れています。探してみてください！", now),
            (2, "今日午食何食べよう", "キムチチゲ食べようか？ いや、チェヨクボックム？ 推奨くれ...", now),
            (3, "非密プロジェクト進行中", "次週に重要な発表があります。絶対外部に流出禁止。", now),
            (1, "SQL Injection 実習用投稿文", "このブログの複数の機能で SQL Injection が可能です。直接探してみてください。 flag は secrets テーブルにあります。", now),
        ]
        c.executemany(
            "INSERT INTO posts (user_id, title, content, created_at) VALUES (?, ?, ?, ?)",
            posts
        )

        # Comments (one with XSS payload example)
        comments = [
            (1, 1, "本当に有用なサイトですね！", now),
            (2, 2, "私はキムチチゲ推奨！", now),
            (3, 1, "<script>alert('XSS テスト')</script> コメントにスクリプトを入れるとどうなるかな？", now),
            (1, 4, "この文の content をよく見るとヒントがあるかも？", now),
        ]
        c.executemany(
            "INSERT INTO comments (post_id, user_id, content, created_at) VALUES (?, ?, ?, ?)",
            comments
        )

        # Secrets - the real treasure for advanced SQLi
        secrets = [
            (1, "admin", "root password hint: p@ssw0rd_is_not_this", "FLAG{SQLi_UNION_is_classic}"),
            (2, "sumi", "私が好きな人は铁水だよ...絶対発覚れないで", "FLAG{BLIND_SQLi_IS_POWERFUL}"),
            (3, "admin", "VulnBoard DB backup password: vulnboard2025!backup", "FLAG{TIME_BASED_SQLi_MASTER}"),
            (4, "chulsu", "水美に高白しようとする勇気がない...", "FLAG{SECOND_ORDER_SQLi}"),
        ]
        c.executemany(
            "INSERT INTO secrets (id, owner, secret, flag) VALUES (?, ?, ?, ?)",
            secrets
        )

        # Sample file record
        c.execute(
            "INSERT INTO files (user_id, filename, original_name, uploaded_at) VALUES (?, ?, ?, ?)",
            (1, "notice.txt", "公告事項.txt", now)
        )

        # Create a real file in uploads
        with open(os.path.join(app.config['UPLOAD_FOLDER'], "notice.txt"), "w", encoding="utf-8") as f:
            f.write("VulnBoard 管理者公告\n管理者パスワードは絶対変えないでください: admin123!@#\n")

    conn.commit()
    conn.close()
    print("[+] Database initialized with seed data.")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# Helper: very vulnerable query executor (for teaching)
# ============================================================
def execute_vulnerable_query(query):
    """
    WARNING: This is intentionally vulnerable.
    We use this for demonstrating raw SQL concatenation.
    """
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute(query)
        rows = c.fetchall()
        return rows, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


# ============================================================
# Routes
# ============================================================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/board')
def board():
    """ 投稿板一覧 - 検索機能含む (強力な SQLi ポイント) """
    keyword = request.args.get('q', '')
    conn = get_db()
    c = conn.cursor()

    if keyword:
        # VULNERABLE: Classic search SQLi (LIKE with concatenation)
        # Try: ' OR '1'='1' --
        # Try: ' UNION SELECT 1,username,password,4 FROM users --
        query = f"SELECT p.id, p.title, p.content, u.nickname, p.created_at FROM posts p JOIN users u ON p.user_id = u.id WHERE p.title LIKE '%{keyword}%' OR p.content LIKE '%{keyword}%' ORDER BY p.id DESC"
        rows, error = execute_vulnerable_query(query)
        posts = rows if rows else []
    else:
        c.execute("""
            SELECT p.id, p.title, p.content, u.nickname, p.created_at 
            FROM posts p 
            JOIN users u ON p.user_id = u.id 
            ORDER BY p.id DESC
        """)
        posts = c.fetchall()
        error = None

    conn.close()
    return render_template('board.html', posts=posts, keyword=keyword, error=error)


@app.route('/post/<int:post_id>')
def view_post(post_id):
    """ 個別投稿を見る - ID 基盤 SQLi (一番現実的なパターン) """
    conn = get_db()
    c = conn.cursor()

    # VULNERABLE: Direct ID injection point
    # Normal: /post/1
    # Attack: /post/1' OR '1'='1   or   /post/99999 UNION ...
    # Also good for error-based and union-based
    query = f"SELECT p.id, p.title, p.content, u.nickname, u.id as author_id, p.created_at FROM posts p JOIN users u ON p.user_id = u.id WHERE p.id = {post_id}"
    rows, error = execute_vulnerable_query(query)

    post = rows[0] if rows else None
    comments = []

    if post:
        # VULNERABLE comment loading (also injectable via other means)
        c.execute("SELECT c.id, c.content, u.nickname, c.created_at FROM comments c JOIN users u ON c.user_id = u.id WHERE c.post_id = ?", (post['id'],))
        comments = c.fetchall()

    conn.close()
    return render_template('post.html', post=post, comments=comments, error=error, post_id=post_id)


@app.route('/post/<int:post_id>/comment', methods=['POST'])
def add_comment(post_id):
    """ コメント書き込み - Stored XSS + SQLi 可能 """
    if 'user_id' not in session:
        flash("ログインが必要です。")
        return redirect(url_for('login'))

    content = request.form.get('content', '')

    conn = get_db()
    c = conn.cursor()
    now = datetime.now().isoformat()

    # VULNERABLE: content is stored as-is (no escaping) → stored XSS
    # Also later can be used in other queries for second-order SQLi
    c.execute(
        "INSERT INTO comments (post_id, user_id, content, created_at) VALUES (?, ?, ?, ?)",
        (post_id, session['user_id'], content, now)
    )
    conn.commit()
    conn.close()

    flash("コメントが登録されました。 (Stored XSS テスト可能)")
    return redirect(url_for('view_post', post_id=post_id))


@app.route('/write', methods=['GET', 'POST'])
def write_post():
    if 'user_id' not in session:
        flash("ログインが必要です。")
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title', '')
        content = request.form.get('content', '')

        conn = get_db()
        c = conn.cursor()
        now = datetime.now().isoformat()
        c.execute(
            "INSERT INTO posts (user_id, title, content, created_at) VALUES (?, ?, ?, ?)",
            (session['user_id'], title, content, now)
        )
        conn.commit()
        new_id = c.lastrowid
        conn.close()

        flash("投稿が登録されました。")
        return redirect(url_for('view_post', post_id=new_id))

    return render_template('write.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ ログイン - 最も高典的で強力な SQLi 進入点 """
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        conn = get_db()
        c = conn.cursor()

        # VULNERABLE: Classic authentication bypass
        # Payload: admin' -- 
        # Payload: ' OR '1'='1' --
        # Payload: admin' OR '1'='1' LIMIT 1 --
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        rows, err = execute_vulnerable_query(query)

        if rows and len(rows) > 0:
            user = rows[0]
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = bool(user['is_admin'])
            flash(f"歓迎します、{user['nickname']}さん！")
            conn.close()
            return redirect(url_for('board'))
        else:
            error = "ログイン失敗。 SQLiで建回してみてください！"
            conn.close()

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    flash("ログアウトされました。")
    return redirect(url_for('index'))


@app.route('/profile')
@app.route('/profile/<username>')
def profile(username=None):
    """ プロファイル参照 - IDOR / Parameter Tampering 実習 """
    if username is None:
        if 'username' not in session:
            return redirect(url_for('login'))
        username = session['username']

    conn = get_db()
    c = conn.cursor()

    # VULNERABLE: 直接 username で取得 (あらゆる権限チェックなし)
    # /profile/admin または /profile/sumi で直接移動可能
    # 後で /profile?user= で変更して param tamper 実習も可能に拡張
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()

    # 使用者の posts
    if user:
        c.execute("SELECT id, title, created_at FROM posts WHERE user_id = ? ORDER BY id DESC", (user['id'],))
        user_posts = c.fetchall()
    else:
        user_posts = []

    conn.close()
    return render_template('profile.html', user=user, user_posts=user_posts, viewed_username=username)


@app.route('/search')
def search():
    """ 別途検索ページ (bookの各種技法実習用) """
    q = request.args.get('q', '')
    results = []
    error = None

    if q:
        # VULNERABLE: Another search point, different from board
        query = f"SELECT id, title, content FROM posts WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'"
        rows, err = execute_vulnerable_query(query)
        if err:
            error = f"エラー発生 (これでエラー基盤 SQLi 実習しよう): {err}"
        else:
            results = rows or []

    return render_template('search.html', results=results, q=q, error=error)


@app.route('/admin')
def admin_panel():
    """ 管理者ページ - Broken Access Control 実習の正式 """
    # VULNERABLE: セッションの is_admin だけチェック。 URLで直接アクセス可能。
    # Bypass 方法:
    # 1. SQLiでログインしながら is_admin=1 セッション強制
    # 2. Burpでクッキー/セッション変更
    # 3. /admin?admin=1 のような param 追加 (意図的にチェックしていない)
    if not session.get('is_admin'):
        # Weak check - easy to bypass with SQLi or direct access after tampering
        flash("管理者のみアクセス可能です。 (ヒント: SQLiやセッション変更で建回しよう)")
        return redirect(url_for('board'))

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    all_users = c.fetchall()
    c.execute("SELECT * FROM secrets")
    all_secrets = c.fetchall()
    conn.close()

    return render_template('admin.html', users=all_users, secrets=all_secrets)


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
def admin_delete_user(user_id):
    """ 管理者機能 - 追加 broken access + IDOR """
    if not session.get('is_admin'):
        return "権限なし", 403

    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    flash(f"ユーザー {user_id} 削除試行されました (実際は cascade されていない)")
    return redirect(url_for('admin_panel'))


# ============================================================
# File upload (basic, for Ch09 file upload chapter)
# ============================================================
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'user_id' not in session:
        flash("ログイン後利用してください。")
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash("ファイルがありません。")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("選択されたファイルがありません。")
            return redirect(request.url)

        if file:
            # VULNERABLE: filename sanitization weak (for later path traversal / upload bypass)
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)

            conn = get_db()
            c = conn.cursor()
            c.execute(
                "INSERT INTO files (user_id, filename, original_name, uploaded_at) VALUES (?, ?, ?, ?)",
                (session['user_id'], filename, file.filename, datetime.now().isoformat())
            )
            conn.commit()
            conn.close()

            flash(f"ファイルアップロード成功: {filename} (ウェブシェルアップロード 実習可能地点)")
            return redirect(url_for('upload_file'))

    # List uploaded files (also vulnerable listing)
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT f.*, u.username FROM files f JOIN users u ON f.user_id = u.id ORDER BY f.id DESC")
    files = c.fetchall()
    conn.close()

    return render_template('upload.html', files=files)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    # VULNERABLE: Direct file serving without proper access control or type check
    # Later chapters: path traversal like /uploads/../../app.py or webshell
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ============================================================
# Command injection simulation point (Ch05)
# ============================================================
@app.route('/tools/ping', methods=['GET', 'POST'])
def ping_tool():
    """ 意図的に脆弱な ping ツール (OS Command Injection 実習) """
    result = None
    cmd = None
    if request.method == 'POST':
        host = request.form.get('host', '127.0.0.1')
        # VULNERABLE: 直接シェル命令に挿入
        # Windows: 127.0.0.1 & whoami
        # または 127.0.0.1 | dir
        cmd = f"ping -n 1 {host}"   # Windows ping
        # 実際実行 (危険だが学習用)
        try:
            import subprocess
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=5)
            result = output.decode('utf-8', errors='ignore')
        except Exception as e:
            result = f"実行結果 (エラー含む): {str(e)}"

    return render_template('ping.html', result=result, cmd=cmd)


# ============================================================
# Debug / Utility for learning
# ============================================================
@app.route('/debug/db')
def debug_db():
    """ 学習用: 現在 DB 状態を見れるように作った (実際は隠さなければならない) """
    conn = get_db()
    c = conn.cursor()
    tables = {}
    for table in ['users', 'posts', 'comments', 'secrets', 'files']:
        c.execute(f"SELECT * FROM {table}")
        tables[table] = [dict(row) for row in c.fetchall()]
    conn.close()
    return render_template('debug_db.html', tables=tables)


@app.route('/reset')
def reset_db():
    """ 便宜機能: DB 初期化 (実習中に壊した時) """
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    session.clear()
    flash("データベースが初期化されました。もう一度ログインしてください。 (admin / admin123!@#)")
    return redirect(url_for('index'))


# ============================================================
# Templates are in templates/ folder (we will create them)
# ============================================================

if __name__ == '__main__':
    init_db()
    print("=" * 60)
    print("VulnBoard (脆弱投稿板) 開始")
    print("接続アドレス: http://127.0.0.1:5002")
    print("Burp Suiteをケンにして全ての攻撃を実習しましょう！")
    print("DB 初期化: /reset")
    print("ヒント/チャレンジ: vulnboard/HACKING_CHALLENGES.md 参照")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5002, debug=True)
