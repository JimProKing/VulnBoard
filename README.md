# VulnBoard

**웹 해킹 실습용 취약 웹사이트 + Burp 연습 프로젝트**

크리핵티브의 《한 권으로 끝내는 웹 해킹 바이블》을 공부하면서 만들어본 프로젝트입니다.

책만 읽다 보니 너무 지루해서, "직접 만들어서 해킹하면서 배우자"는 생각으로 시작했습니다. 
책의 구조를 따라가며 SQL Injection, XSS, IDOR, 파일 업로드 등 주요 취약점을 실습할 수 있는 하나의 메인 타겟(VulnBoard)과 기초 예제들을 만들었어요.

---

## 🚀 시작하기

```bash
git clone https://github.com/JimProKing/VulnBoard.git
cd VulnBoard/webhacking-bible-lab/vulnboard
pip install -r ../../requirements.txt
python app.py
```

http://127.0.0.1:5002 에서 접속

**꼭 Burp Suite를 켜고** 하세요. 이 프로젝트의 진짜 목적은 Burp로 직접 요청을 가로채고 수정하면서 공격하는 감각을 기르는 거예요.

기본 로그인 정보:
- admin / admin123!@#
- chulsu / test123

---

## 🎯 주요 실습 내용

- **VulnBoard** (메인)
  - 로그인 우회 (SQLi)
  - 검색/게시글 SQL Injection (UNION, Blind, Time-based)
  - Stored XSS (댓글)
  - IDOR / 파라미터 변조
  - Broken Access Control (/admin)
  - 파일 업로드 취약점
  - OS Command Injection (Ping 도구)

- **01-basics**: 입력값 검증 미흡의 기본 개념 (Ch01)
- **02-http-burp**: HTTP와 Burp Suite 기초 다지기 (Ch02)

모든 취약한 부분에는 코드에 주석으로 표시해뒀습니다.

---

## 📝 공부하면서 남긴 노트

`vulnboard/HACKING_CHALLENGES.md` 에 레벨별로 챌린지와 힌트를 정리해놨습니다.

책을 따라가면서 실제로 공격해보고, 에러 메시지 보고, 컬럼 수 맞추고, flag 뽑는 과정을 직접 경험하려고 했어요.

`/reset` 경로로 DB를 언제든 초기화할 수 있게 해놔서 실험하기 편하게 만들었습니다.

---

## ⚠️ 주의사항

- 이건 **순수 학습용**입니다. 실제 서비스에는 절대 사용하지 마세요.
- 공부 목적으로만 활용해주세요.

---

## 📁 폴더 구조

```
webhacking-bible-lab/
├── 01-basics/          # 기본 개념 실습 (파라미터 변조 등)
├── 02-http-burp/       # HTTP + Burp 마스터
├── vulnboard/          # 메인 실습 타겟 (강력 추천)
├── README.md
└── requirements.txt
```

---

공부하면서 만든 거라 완벽하진 않지만, 비슷하게 공부하시는 분들께 조금이라도 도움이 되길 바랍니다.

Burp 열심히 켜고 하세요!