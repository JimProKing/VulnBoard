# 02-http-burp : HTTP + Burp Suite 완전 정복 (책 Ch02 핵심)

이 챕터는 **웹 해킹 전체 과정에서 가장 중요한 기초**입니다.  
크리핵티브 책에서도 Ch02를 상당히 자세히 다룹니다.

## 학습 목표
- HTTP 요청/응답의 모든 구성 요소를 정확히 이해
- **Burp Suite**로 모든 웹 트래픽을 가로채고, 수정하고, 재전송하는 근육 기억 만들기
- "사용자 입력값이 어떻게 서버까지 가는지"를 시각적으로 체감
- 파라미터 변조의 맛보기 (책 Ch01 마지막 예시 재현)

## 0. 사전 준비 (Windows)

### Burp Suite Community 설치
1. https://portswigger.net/burp/communitydownload 접속
2. Burp Suite Community Edition 다운로드 + 설치
3. 처음 실행하면 CA 인증서 설치하라고 나옴 → **반드시 설치** (브라우저가 Burp가 중간에 끼어드는 걸 신뢰하게 만듦)

### 브라우저 프록시 설정 (강력 추천: FoxyProxy)
- Chrome에 **FoxyProxy** 확장 설치
- 새 프록시 추가:
  - Title: Burp
  - Proxy IP: 127.0.0.1
  - Port: 8080
  - Pattern: `*` (또는 원하는 도메인만)
- 필요할 때만 ON/OFF 할 수 있게 만들기

수동 설정도 가능하지만, 매번 설정 바꾸는 게 귀찮아서 FoxyProxy 추천.

## 1. 앱 실행

```powershell
# lab 루트에서
cd 02-http-burp
python app.py
```

브라우저에서 **http://127.0.0.1:5001** 열기 (Burp OFF 상태로 먼저 구조 파악)

## 2. 반드시 해봐야 할 실습 (순서대로)

### 실습 A: GET 요청 + 파라미터 변조 (책 초반 예시 그대로)
1. Burp를 **Intercept ON** 상태로 만들기
2. 메인 페이지에서 "회원 정보 보기" 폼 전송 (user=chulsu)
3. Burp에서 요청이 멈춤 → **Headers, Params 탭 자세히 보기**
   - GET /profile?user=chulsu HTTP/1.1
   - Host, User-Agent, Cookie, Accept 등 헤더 관찰
4. `user=chulsu` 를 `user=sumi` 로 **직접 수정** 후 Forward
5. 브라우저에 **수미의 전화번호**가 나오는지 확인

**성공 기준**: 수미의 전화번호(010-9876-5432)를 내 눈으로 확인.

### 실습 B: POST 요청 바디 보기
1. 로그인 폼으로 chulsu / test123 전송
2. Burp에서 **요청 바디** 확인 (application/x-www-form-urlencoded)
   - username=chulsu&password=test123
3. Repeater로 보내서 password 값을 아무거나 바꿔서 여러 번 시도해보기

### 실습 C: 쿠키 탈취 및 세션 하이재킹 맛보기
1. 로그인 성공 후 "내 정보 보기" 링크 클릭
2. Burp History에서 `/myinfo` 요청 찾기 → Request에 `Cookie: session_user=chulsu` 가 있는지 확인
3. Repeater로 복사
4. Cookie 값을 `session_user=admin` 으로 바꿔서 Go
5. 관리자 정보가 나오는지 확인

이게 바로 나중에 **세션 하이재킹**으로 발전합니다 (XSS 챕터에서 본격 등장).

### 실습 D: 디버그 페이지 활용
`/debug/request` 페이지로 가서 현재 요청의 모든 정보를 JSON처럼 볼 수 있음.  
Burp 없이도 대략적인 구조 파악에 좋지만, **진짜 실력은 Burp로 키운다**.

## 3. Burp 핵심 기능 (이 챕터에서 집중할 것)

| 기능       | 어디서 쓰나                  | 이번 실습에서 할 일                     |
|------------|------------------------------|-----------------------------------------|
| Proxy      | 모든 트래픽 가로채기         | Intercept ON/OFF, Forward              |
| HTTP History | 과거 요청/응답 기록       | 어떤 요청이 언제 갔는지 복기            |
| Repeater   | 같은 요청을 여러 번 변조     | 파라미터/쿠키/헤더 마음대로 바꿔보기   |
| Decoder    | URL 인코딩, Base64 등        | 나중에 payload 만들 때 유용             |
| Intruder   | 자동화 공격 (나중에)         | 아직은 스킵, SQLi/XSS 때 본격 사용     |

## 4. 이 앱에서 발견할 수 있는 "취약한 코드" 포인트

`app.py`를 열어서 다음을 직접 찾아보세요:

- `/profile` 라우트의 `username = request.args.get("user", ...)` 후 바로 DB 조회
- 아무런 권한 체크 없음 (`현재 로그인한 사람이 이 user를 볼 수 있는가?`)
- `/myinfo` 에서 쿠키만으로 인증 (서명 없음, 그냥 username)

**책의 핵심 메시지**:  
"대부분의 취약점은 사용자 입력값에 대한 검증 미흡에서 시작한다."

## 5. 자가 점검 퀴즈 (답은 스스로 생각해보기)

1. HTTP 요청에서 "파라미터"는 GET과 POST 중 어디에 주로 들어가는가?
2. Burp Repeater와 브라우저에서 직접 URL 치는 것의 가장 큰 차이점은?
3. `session_user=chulsu` 쿠키를 `session_user=admin`으로 바꾸는 행위는 어떤 공격에 해당하는가?
4. 왜 웹 애플리케이션은 "사용자 입력"을 받을 수밖에 없는 구조인가? (책 1.1~1.2 참고)
5. httponly 쿠키를 설정했는데도 왜 쉽게 탈취당할 수 있는가? (XSS와 연계해서 나중에)

## 다음 단계

이 실습이 끝나면:
- Burp 없이 웹 해킹을 한다는 건 상상도 할 수 없는 상태가 되어야 함
- "이 요청을 가로채서 이렇게 바꾸면 어떻게 될까?" 하는 생각이 자동으로 들어야 함

준비되면 말해.  
**"02 끝냈어. 다음으로 넘어가자"** 또는 **"02에서 쿠키 하이재킹이 안 돼. 도와줘"** 라고 하면 다음으로 진행하거나 같이 디버그한다.

---

**공식 책 예제 참고**: 저자의 GitHub에 insecure_board가 있지만, 이건 Tomcat+MySQL이라 무거움.  
여기서는 가볍게 Flask로 동일한 개념을 먼저 체득하는 게 목표.
