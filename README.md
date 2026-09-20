# THREAD MARKET — 쇼핑몰 프런트 + AI 제작 백엔드

이 폴더 전체를 GitHub 저장소에 올린 뒤 Railway에 연결할 수 있습니다.
실제 API 키는 포함되어 있지 않습니다. `.env.example`은 환경 변수 이름 안내용입니다.

## 1. 무엇이 들어 있나요?

| 파일 | 역할 |
|---|---|
| `public/index.html` | 쇼핑몰 전체 프런트. HTML/CSS/JS/샘플 이미지가 모두 포함된 한 파일 |
| `app.py` | FastAPI 서버, SQLite, 로그인, AI 제작 작업, 다운로드, 상품 게시 |
| `admin.py` | 판매자 승인/해제, 독점 이용 권한, 다운로드 초기화 CLI |
| `requirements.txt` | 설치할 Python 라이브러리 |
| `Dockerfile` | Railway에서 사용할 서버 실행 환경 |
| `railway.toml` | 빌드·헬스체크·재시작 설정 |
| `.env.example` | 필요한 환경 변수 안내 (실제 키 없음) |
| `.gitignore`, `.dockerignore` | 비밀 파일 및 사용자 데이터 제외 |
| `tests/test_flow.py` | 외부 API 비용 없이 수행하는 통합 테스트 |
| `API.md` | 프런트·백엔드 요청/응답 규칙 |
| `DEPLOY_HANDOFF.md` | 다른 개발자나 AI에게 전달할 배포 요청문 |

## 2. 구현한 기능과 아직 연결할 기능

### 동작하는 기능

- 반응형 쇼핑몰 메인, 카테고리·검색·정렬, 상품 상세, 색상·사이즈 선택
- 관심 상품과 장바구니 (이 브라우저에 저장)
- 주문서 UI, 배송지 입력 검증, 서버 기준 상품 금액·재고·배송비 견적
- 회원가입·로그인·로그아웃, HttpOnly 쿠키 세션
- 구매자/판매자 계정 구분, 관리자 판매자 승인
- 사진 2장 접수, 파일 형식·크기 확인, EXIF 제거 및 이미지 정규화
- OpenAI 이미지 분석/상품 설명 생성 + 선택적 이미지 편집
- 비동기 제작 및 작업 내역/상태 확인
- 무료 워터마크, 서버 측 1회 HTML 다운로드 제한
- 독점 제작 이용 권한 확인 (관리자가 수동 부여하는 MVP)
- 결과를 검토한 뒤 판매가·옵션별 재고 입력 및 쇼핑몰 상품 게시
- 다른 계정의 제작 결과 접근 차단
- Railway Volume에 SQLite와 업로드·생성 파일 보관

### 별도 구현·설정이 필요한 기능

- **PG 실제 결제, 결제 웹훅, 환불, 주문 재고 차감/예약**
- 주문 접수 이후 배송·송장·판매자 수수료 정산
- 이메일 인증, 비밀번호 찾기/재설정, 관리자 웹 화면
- 쿠폰·리뷰·택배사 연동 등 확장 기능
- 실제 사업자 정보, 고객센터, 배송·반품 정책, 이용약관, 개인정보 처리방침
- 이미지 원본과 AI 결과의 상품 일치 여부 검수

결제 미연동 상태에서 허위 주문 완료를 표시하지 않습니다.
현재 `/api/checkout/quote`는 `checkoutEnabled: false`를 반환하고 `/api/orders` POST는 503을 반환합니다.
`CHECKOUT_ENABLED=true`만 넣어도 결제가 활성화되지 않습니다. 결제·재고·웹훅 코드를 먼저 구현해야 합니다.
프런트의 주문·결제 연결점은 준비되어 있으며 `API.md`에 계약을 적었습니다.

## 3. HTML만 먼저 확인하기

별도 제공된 `thread-market.html` 또는 `public/index.html`을 더블클릭하면 **demo 모드**로 열립니다.
구매 흐름은 샘플 상품으로 체험하며 실제 계정을 만들거나 결제하지 않습니다.
샘플 상품의 사진, 가격, 문구는 가상의 디자인 예시입니다. 판매용 상품 정보로 사용하지 마세요.
디자인 체험의 사진 두 장 결과는 원본을 배치한 것이며 AI 생성 결과가 아닙니다.

프런트가 다른 서버에 있다면 HTML 안에서 다음 부분을 변경하세요.

```js
const CONFIG=Object.assign({
  mode:'api',
  apiBase:'https://본인-백엔드.up.railway.app',
  // 나머지 설정 유지
},window.THREAD_RUNTIME||{});
```

함께 제공한 백엔드의 `/`에서 HTML을 열면 서버가 자동으로 `api` 모드를 적용합니다.
같은 서버에서 프런트·백엔드를 제공하는 구성이 쿠키/CORS 설정이 가장 간단합니다.
다른 도메인을 쓰면 HTTPS, CORS, 서드파티 쿠키 정책을 함께 확인해야 합니다.
이미 생성한 백엔드가 있다면 `API.md`와 그 백엔드의 경로·필드명을 비교해 프런트 `request()` 호출부를 맞추세요.

## 4. Windows에서 비용 없이 로컬 실행

Python 3.12 설치 후 이 폴더에서 PowerShell을 엽니다.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:COOKIE_SECURE="false"
$env:ALLOWED_ORIGINS="http://localhost:8000,http://127.0.0.1:8000"
$env:GENERATION_MODE="mock"
$env:DATA_DIR="$PWD\data"
.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000 --workers 1
```

브라우저에서 `http://localhost:8000`에 접속하세요.
`mock`은 실제 서버·인증·저장·다운로드·상품 게시 흐름을 확인하되 OpenAI를 호출하지 않습니다.
공개 API 상품 목록은 초기에는 비어 있습니다. 판매자 가입 → 승인 → 제작 → 검토 → 게시하면 목록에 나타납니다.
샘플 이미지와 상품을 실제 상품으로 자동 등록하지 않습니다.

판매자로 가입한 뒤 **다른 PowerShell 창**에서 같은 폴더로 이동하고 실행하세요.

```powershell
$env:DATA_DIR="$PWD\data"
.\.venv\Scripts\python.exe admin.py approve-seller seller@example.com
```

승인 후 쇼핑몰을 새로고침하세요.

## 5. 실제 OpenAI 연결

서버 환경 변수에 아래 값을 등록한 후 서버를 재시작합니다.

```text
OPENAI_API_KEY=본인_비밀키
GENERATION_MODE=ai
TEXT_MODEL=gpt-4.1-mini
IMAGE_MODEL=gpt-image-1.5
AI_IMAGE_EDIT=true
```

- 키를 HTML, GitHub 코드, README, 채팅에 붙이지 마세요.
- 모델 이름은 환경 변수로 변경할 수 있습니다. 계정에서 해당 모델 사용 권한과 API 결제 설정이 필요합니다.
- 기본 실행 한 번은 텍스트/사진 분석 1회 + 이미지 편집 1회입니다. 이미지 생성만 실패해도 작업은 실패로 남습니다.
- `AI_IMAGE_EDIT=false`이면 AI는 사진 분석·설명만 만들고 이미지에는 원본을 사용합니다.
- 로고/패턴 보존 프롬프트가 있어도 동일성을 보장하지 않습니다. 결과를 비교 검토한 후 게시하세요.
- SDK 자동 재시도는 꺼두었습니다. 타임아웃·서버 종료 시 상위 API에서 비용이 발생했을 수 있으므로 무조건 재요청하지 마세요.
- 개발 중에는 `mock`을 사용하고 작은 수량으로 실제 모델을 검증하세요.

## 6. Railway 배포 순서

1. **이 폴더 전체**를 새 GitHub 저장소 루트에 올립니다. `.env`나 `data/`는 올리지 않습니다.
2. Railway에서 새 프로젝트를 만들고 해당 GitHub 저장소를 연결합니다.
3. Dockerfile을 이용해 빌드하도록 합니다. 시작 명령은 Dockerfile에 이미 있습니다.
4. 서비스에 **Volume을 추가하고 `/data`에 마운트**합니다.
5. 서비스의 공개 도메인을 생성합니다.
6. Railway Variables에 다음 값을 설정합니다.

```text
OPENAI_API_KEY=본인_비밀키
GENERATION_MODE=ai
TEXT_MODEL=gpt-4.1-mini
IMAGE_MODEL=gpt-image-1.5
AI_IMAGE_EDIT=true
DATA_DIR=/data
ALLOWED_ORIGINS=https://본인-서비스.up.railway.app
COOKIE_SECURE=true
COOKIE_SAMESITE=lax
FREE_DAILY_LIMIT=3
GLOBAL_DAILY_LIMIT=30
MAX_PENDING_JOBS=10
CHECKOUT_ENABLED=false
```

7. 재배포 후 공개 URL에서 쇼핑몰이 열리는지 확인합니다.
8. `공개URL/api/health`에 `{"ok":true,...}`가 나오면 서버 실행 확인입니다.
9. 본인 판매자 계정으로 가입합니다.
10. **실제 배포 컨테이너의 셸/SSH**에서 다음 명령을 실행해 판매자를 승인합니다.

```bash
python admin.py approve-seller seller@example.com
```

로컬에서 `railway run`만 실행하면 원격 Volume의 SQLite가 아니라 로컬 파일에 접근할 수 있습니다.
승인 명령은 반드시 운영 서비스의 `/data`가 마운트된 실행 환경에서 수행하세요.

11. 사진 2장으로 제작 후 결과 검토 → 판매가·재고 입력 → 게시를 확인합니다.
12. 연결된 배포 브랜치로 push할 때 자동배포되도록 Railway의 소스/배포 설정을 확인합니다.

이 전달물에서 GitHub 저장소 생성, Railway 프로젝트 생성, 환경 변수 등록, 실제 배포는 수행하지 않았습니다.
배포 담당자에게 `DEPLOY_HANDOFF.md`를 함께 전달하면 됩니다.

## 7. 판매자 권한 관리

```bash
# 승인 / 승인 해제
python admin.py approve-seller seller@example.com
python admin.py revoke-seller seller@example.com

# 관리자 확인 후 독점 제작 권한 30일 부여 (실제 결제를 하지 않음)
python admin.py grant-paid seller@example.com --days 30

# 다운로드가 전송 중 끊겼을 때 관리자가 확인 후 횟수 복구
python admin.py reset-download job_작업ID
```

무료 다운로드는 응답 전송을 시작할 때 횟수가 차감됩니다. 네트워크 실패 시 위 복구 명령을 이용하세요.
무료 출력 파일에는 픽셀 워터마크가 포함되지만 DRM이 아니므로 복제 방지 기능을 의미하지 않습니다.

## 8. 운영 범위와 저장

- **단일 서비스 인스턴스 / uvicorn worker 1개**로 실행하세요.
- SQLite DB와 이미지는 `DATA_DIR`에 저장합니다. Railway Volume이 없으면 재배포 시 데이터가 사라질 수 있습니다.
- DB와 이미지가 함께 복원될 수 있도록 Volume 백업 정책을 설정하세요.
- 제작 중 서버를 재시작하면 해당 작업은 실패로 표시됩니다. 과금 중복 방지를 위해 자동 재실행하지 않습니다.
- `FREE_DAILY_LIMIT`은 현재 무료·독점 모두 포함한 계정별 UTC 날짜 생성 한도입니다. 실패 작업도 횟수에 포함됩니다.
- 기본 전역 한도 30건/일, 대기열 10건입니다. 한도를 올리기 전에 비용과 서버 처리량을 확인하세요.
- 업로드는 장당 10MB/3,200만 화소까지 받고 2,400px 범위 JPEG로 정규화합니다.
- 세션은 7일이며 DB에는 토큰 해시만 저장합니다. 비밀번호는 scrypt 해시로 저장합니다.
- POST 요청은 등록된 Origin만 허용합니다. curl/Postman은 `Origin` 헤더를 넣어 테스트하세요.
- 브라우저의 대기 취소는 서버의 이미 시작된 AI 작업을 취소하지 않습니다. 제작 내역에서 다시 확인하세요.
- 이 MVP에는 자동 보관기한 삭제, 이메일 인증, 비밀번호 재설정, 판매자 정산이 없습니다.
- 여러 서버로 확장하려면 공유 DB, 객체 저장소, 별도 작업 큐, 분산 제한을 적용해야 합니다.
- `bodyLimit`은 요청 본문을 최대 22MB까지 메모리에 보관합니다. 대규모 업로드 트래픽에는 앞단 제한/스트리밍 저장을 추가하세요.

## 9. 테스트

```powershell
.\.venv\Scripts\python.exe tests/test_flow.py
```

mock 통합 테스트: 로그인·승인, 게시 동의, 유료 권한 차단, 이미지 접수, 비동기 완료,
다른 사용자 접근 차단, 다운로드 제한, HTML 출력 이스케이프, 상품 게시, 가격/재고 재확인,
미연동 결제 차단, 로그아웃.

제공 전 위 테스트와 프런트 DOM 동작 테스트를 통과했습니다.
실제 OpenAI 유료 호출, 실제 PG, 실기기 브라우저 시각 QA, Railway 배포는 수행하지 않았습니다.

## 10. 참고한 공식 문서

- [OpenAI 이미지 생성/편집](https://developers.openai.com/api/docs/guides/image-generation)
- [OpenAI 구조화 출력](https://developers.openai.com/api/docs/guides/structured-outputs)
- [FastAPI 파일 업로드](https://fastapi.tiangolo.com/tutorial/request-files/)
- [Railway FastAPI 배포](https://docs.railway.com/guides/fastapi)
- [Railway Volume](https://docs.railway.com/volumes)
