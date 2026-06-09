# 🔥 VulnBoard

**"공격 알아야 방어 보인다" — 크리핵티브의 한 권으로 끝내는 웹 해킹 바이블 실전 연습장**

> 책 900페이지 읽기 지루하다고?  
> **그럼 직접 부숴.**  
> Burp 켜고, SQL Injection으로 admin 되는 그 맛을 느껴봐.

VulnBoard는 **의도적으로 취약한** 하나의 웹사이트 + 기초 예제들로 구성된 **안전한 해킹 놀이터**야.

---

## 🚀 30초 만에 시작하기

```bash
git clone https://github.com/JimProKing/VulnBoard.git
cd VulnBoard/webhacking-bible-lab/vulnboard
pip install -r ../../requirements.txt
python app.py
```

브라우저에서 http://127.0.0.1:5002 열고  
**Burp Suite** 켜는 거 잊지 마 (이게 진짜 주인공임)

기본 계정:
- `admin` / `admin123!@#`
- `chulsu` / `test123`

---

## 🎮 주요 챌린지 (HACKING_CHALLENGES.md 필독)

- **Level 1**: 로그인 SQLi로 admin 탈취 (`admin' -- ` 의 맛)
- **Level 2**: 검색에서 UNION으로 secrets 테이블 털기
- **Level 3~5**: 게시글 ID, Blind, Time-based SQLi
- **보너스**: Stored XSS, IDOR, Broken Access Control, 파일 업로드, Command Injection

secrets 테이블에 **FLAG**들이 숨겨져 있어. 다 먹으면 승리.

---

## 🛠️ 들어있는 것들

| 폴더          | 내용                              | 책 매핑          |
|---------------|-----------------------------------|------------------|
| `vulnboard/`  | 메인 취약 게시판 (강추)           | Ch04~Ch11       |
| `01-basics/`  | 왜 웹이 공격 맛집인가?            | Ch01            |
| `02-http-burp`| HTTP + Burp 완전 정복             | Ch02            |

모든 취약점 코드에 `# VULNERABLE:` 주석 달아놨음.  
직접 소스 보면서 "아 이 한 줄 때문에..." 깨달아라.

---

## ⚠️ 진짜 중요한 주의사항

- 이건 **학습용**이야. 실제 서비스에 이런 거 날리면 진짜 감옥 간다.
- `/reset` 누르면 DB가 깨끗해짐. 실험하다 망가뜨려도 OK.
- Burp Repeater를 신처럼 모셔라.

---

## 💡 학습 팁 (크리핵티브 스타일)

1. 무조건 Burp로 모든 요청 가로채기
2. 에러 메시지 무시하지 말기 (그게 네 친구야)
3. "이 쿼리가 실제로 어떻게 생겼을까?" 상상하면서 공격
4. 성공한 페이로드는 Repeater에 저장
5. 막히면 "Level 2에서 컬럼 수가 안 맞아" 라고 말하면 도와줄게

---

## 📦 설치 & 실행 (Windows 기준)

```powershell
# 1. 저장소 클론
git clone https://github.com/JimProKing/VulnBoard.git
cd VulnBoard\webhacking-bible-lab

# 2. 의존성
pip install -r requirements.txt

# 3. VulnBoard 실행 (메인)
cd vulnboard
python app.py
```

---

## 🎉 이 프로젝트가 만들어진 이유

사용자가 "책 읽는 건 재미없고, 웹사이트 직접 만들어서 해킹하면서 공부하고 싶다"고 해서 태어난 프로젝트.

작은 예제 여러 개 대신, **하나의 제대로 된 취약 사이트**를 만들어서 실제 해킹 감각을 키울 수 있게 했다.

공식 책 예제 (Tomcat+JSP)는 무거우니까, 이건 Flask + SQLite로 가볍게 Windows에서도 바로 돌릴 수 있게 만들었음.

---

**이제 가서 admin 계정 털어라.**

그리고 성공하면 나한테 "Level 1 클리어" 라고 말해.  
다음 레벨로 안내해줄게.

해킹 재밌게 하자 🔥

*(이 프로젝트는 크리핵티브 바이블 공부용으로 만들어졌으며, 실제 공격 연습은 절대 금지)*

---

Made with ❤️ (and a lot of `admin' -- `) by Grok for you.
