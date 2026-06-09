# VulnBoard

웹 해킹 공부하면서 직접 만들어 본 실습 프로젝트입니다.

크리핵티브의 《한 권으로 끝내는 웹 해킹 바이블》을 보다가, 책만 읽는 게 너무 지루해서 "그럼 내가 직접 취약한 사이트를 만들어서 연습해보자" 하고 시작한 프로젝트예요.

책에서 나오는 개념들을 실제로 Burp로 공격해보면서 익히려고, Flask로 간단하게 취약한 웹 앱 하나를 메인으로 만들고, 기초 예제도 몇 개 붙였습니다.

---

## 어떻게 시작하나요

```bash
git clone https://github.com/JimProKing/VulnBoard.git
cd VulnBoard/webhacking-bible-lab/vulnboard
pip install -r ../../requirements.txt
python app.py
```

http://127.0.0.1:5002 로 접속하면 됩니다.

**중요**: Burp Suite를 켜고 하세요. 이게 제일 중요합니다.

기본 계정:
- admin / admin123!@#
- chulsu / test123

DB가 망가졌거나 다시 시작하고 싶으면 `/reset` 로 가면 초기화됩니다.

---

## 뭐가 들어있나

- **vulnboard/** : 메인 실습 사이트 (이걸 제일 많이 썼어요)
  - 로그인 SQL Injection
  - 게시판 검색 SQLi (UNION, 에러 기반)
  - 게시글 상세보기에서 ID 기반 인젝션
  - 댓글로 Stored XSS
  - 프로필에서 IDOR 느낌
  - 관리자 페이지 접근 제어 문제
  - 파일 업로드
  - 간단한 Command Injection (ping 도구)

- **01-basics/** : 입력값 검증이 왜 중요한지 간단하게 체감하는 예제
- **02-http-burp/** : HTTP랑 Burp 기본 다지는 용도

코드에 취약한 부분은 대충 주석으로 표시해뒀습니다.

---

## 공부하면서 만든 챌린지 노트

`vulnboard/HACKING_CHALLENGES.md` 에 레벨별로 정리해놨습니다.

책 Ch04(SQL Injection)부터 제대로 막혔어서, 이 사이트로 로그인 우회부터 UNION, Blind까지 직접 부딪혀보려고 만들었어요.

실제로 `/board`에서 검색으로 UNION 써서 secrets 테이블 flag 뽑는 거 성공했을 때 좀 뿌듯했습니다.

---

## 주의

이건 순전히 제 공부용으로 만든 거라, 실제 서비스에 쓰면 안 됩니다.

공부하다가 막히는 부분 있으면 저도 아직 배우는 중이라... 같이 보면서 해보면 좋을 것 같아요.

Burp 열심히 켜고 하시길 바랍니다.