# VulnBoard 해킹 챌린지 가이드
## 크리핵티브 웹 해킹 바이블 실습 매핑 (특히 SQL Injection 중심)

이 사이트는 **의도적으로 취약**하게 만들어졌습니다.  
목표는 "공격 성공"이 아니라, **각 기법의 동작 원리를 몸으로 이해**하는 것입니다.

**강력 추천**: 모든 공격은 Burp Suite를 통해 하세요. Repeater를 애용하세요.

---

## 사전 준비
1. `python app.py` 실행 (포트 5002)
2. Burp 프록시 ON (127.0.0.1:8080)
3. 브라우저 프록시 설정
4. 기본 계정으로 로그인 테스트: `chulsu` / `test123`
5. DB 초기화가 필요하면 `/reset` 방문 (언제든 가능)

---

## SQL Injection 챌린지 (책 Ch04 핵심)

### Level 1: 로그인 우회 (가장 기본)
**목표**: SQL Injection으로 `admin` 계정으로 로그인하기 (비밀번호를 모른 채)

**추천 진입점**: `/login`

**시도할 페이로드 예시** (직접 변형해보기):
- `admin' -- `
- `' OR '1'='1' -- `
- `admin' OR 1=1 -- `

**성공 기준**: "관리자" 권한으로 로그인되고, 상단 네비에 관리자 메뉴가 보이거나 `/admin` 접근이 수월해짐.

**학습 포인트**:
- 인증 쿼리가 어떻게 생겼을지 역으로 유추
- 주석(`-- `, `#`, `/* */`)의 역할
- Burp Repeater로 수십 번 반복 공격하는 습관

---

### Level 2: 게시판 검색 SQLi (UNION 기반)
**진입점**: `/board?q=...` 또는 `/search?q=...`

**목표**:
1. 에러를 발생시켜 컬럼 수 파악 (ORDER BY 10 등)
2. UNION SELECT로 `users` 테이블의 username, password, is_admin 등을 추출
3. `secrets` 테이블의 flag까지 뽑아내기

**유용한 기법**:
- `' UNION SELECT 1,2,3,4,5,6 -- `
- 컬럼 수 맞추기 (에러 메시지가 친절하게 알려줌)
- `secrets` 테이블은 id, owner, secret, flag 컬럼을 가짐

**성공 기준**: secrets 테이블의 FLAG{...} 중 최소 2개 이상 화면에 노출

---

### Level 3: 게시글 ID 기반 SQLi (가장 현실적인 패턴)
**진입점**: `/post/1` , `/post/2` 등

**목표**:
- `/post/1' ` 로 에러 유발
- UNION 또는 에러 기반으로 다른 테이블 데이터 덤프
- 특히 `secrets` 테이블의 flag 추출

**고급**:
- `1 AND 1=2 UNION SELECT ...` (Blind 준비)
- 컬럼 타입 맞추기 (텍스트 vs 숫자)

---

### Level 4: Boolean Blind SQLi
**진입점**: 검색이나 post ID

**목표**: 참/거짓에 따라 페이지 응답(결과 개수, 에러 유무, 내용 길이 등)이 달라지는 것을 이용해 한 글자씩 데이터 추출.

**예시 논리**:
- `1' AND SUBSTR((SELECT password FROM users WHERE username='admin'),1,1)='a' -- `
- 결과가 "있음" vs "없음" 또는 에러 vs 정상으로 구분

**도구 연습**: Burp Intruder로 자동화하거나, 간단한 Python 스크립트 작성 추천.

---

### Level 5: Time-based Blind SQLi
이 앱에서는 DB 레벨 SLEEP이 제한적이라, 앱 레벨에서 조건부 지연을 일부 지원합니다.

**연습 방법**:
- 검색이나 ID에서 특정 조건이 참일 때 응답이 느려지게 만드는 쿼리 작성
- (실제로는 Python time.sleep을 조건에 따라 호출하는 로직이 들어있음)

**성공 기준**: `secrets` 테이블의 `FLAG{TIME_BASED_SQLi_MASTER}` 획득

**참고**: 실제 MySQL/PostgreSQL에서는 `SLEEP()`, `pg_sleep()` 등을 사용합니다. 책에서 자세히 다룹니다.

---

### Level 6: Second-order SQLi (고급)
댓글에 악성 페이로드를 저장한 후, 나중에 그 내용이 다른 쿼리에 사용될 때 발동.

현재 댓글은 주로 Stored XSS 용이지만, 확장해서 second-order를 체험할 수 있는 지점을 더 추가할 수 있습니다.

---

## 다른 챕터 매핑 챌린지

### Broken Access Control / IDOR (Ch11, Ch10)
- `/profile/admin` 또는 `/profile/sumi` 직접 접근
- 로그인 없이, 또는 일반 계정으로 관리자 권한 획득
- `/admin` 페이지 우회 (세션 변조, SQLi로 is_admin=1 만들기, param tamper)

### Stored XSS + 세션 탈취 (Ch06)
- `/post/1` 등에 댓글로 `<script>alert(document.cookie)</script>` 또는 더 나아가 쿠키를 공격자 서버로 전송하는 페이로드 삽입
- (이 사이트는 아직 외부 서버가 없으니, console.log나 alert로 먼저 확인)

### File Upload (Ch09)
- `/upload` 에서 웹쉘(간단한 PHP나 JSP가 아니라, 이 앱은 Python이므로 .py 파일을 업로드하고 직접 호출해보기)
- 파일명에 `../../../` 넣어서 상위 디렉토리 접근 시도
- 업로드 후 `/uploads/파일명` 으로 직접 접근

### OS Command Injection (Ch05)
- `/tools/ping` 페이지
- `127.0.0.1 & whoami` 또는 `127.0.0.1 | dir C:\` 등
- 더 나아가 `& type vulnboard.db` 로 DB 파일 내용 읽기 시도 (가능한가?)

---

## 최종 보스 챌린지 (종합)

1. SQLi만으로 `admin` 계정 탈취 + secrets의 모든 flag 획득
2. Stored XSS로 관리자 세션 쿠키 탈취 시뮬레이션
3. File upload로 악성 파일 업로드 후 실행
4. `/admin` 완전 접근 + 사용자 삭제 기능 악용
5. (보너스) Command Injection으로 서버 정보 최대한 수집

---

## 학습 팁 (책의 정신에 맞게)

- **무조건 Burp Repeater 사용**하세요. 브라우저 주소창만으로는 절대 안 됩니다.
- 에러 메시지를 무시하지 마세요. 컬럼 수, 테이블 구조를 알려주는 최고의 친구입니다.
- `UNION SELECT` 할 때 컬럼 개수와 타입을 맞추는 연습을 많이 하세요.
- Blind는 지루하지만, **한 글자씩 추출하는 로직**을 직접 코드로 짜보는 게 진짜 실력입니다.
- "이 쿼리가 실제로 어떻게 생겼을까?" 를 항상 상상하면서 공격하세요. (책이 강조하는 부분)
- 성공한 공격은 스크린샷 + Repeater 히스토리를 저장해두세요.

---

## 다음 단계 제안

VulnBoard로 충분히 SQLi를 파고들었다 싶으면:
- 책의 나머지 챕터(XSS, CSRF, 파일 업로드 상세 등) 매핑해서 더 복잡한 취약점을 추가하거나
- 공식 예제(insecure_board JSP)를 Docker로 띄워서 비교해보기
- 실제 CTF 문제나 PortSwigger Web Security Academy로 이동

지금은 **이 한 사이트를 철저히 파괴**하는 데 집중하세요.

막히는 부분 있으면 언제든 "Level 3에서 UNION 컬럼 수가 안 맞아" 또는 "admin으로 로그인했는데 /admin이 안 열려" 라고 말해주세요. 같이 해결하겠습니다.

행운을 빕니다. (그리고 재미있게 하세요!)
