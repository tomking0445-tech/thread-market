# API 연결 규칙

같은 서비스에서 `GET /`는 쇼핑몰 HTML, `/api/*`는 JSON 또는 이미지/HTML 파일을 제공합니다.
프런트는 `fetch(..., {credentials:'include'})`를 사용합니다.
모든 POST 요청은 ALLOWED_ORIGINS에 등록된 Origin 헤더가 필요합니다.
실제 API 키는 서버만 사용합니다.

## 계정

| 경로 | 요청 | 응답 |
|---|---|---|
| POST `/api/auth/signup` | `{email,name,password,role:"customer" 또는 "seller"}` | `{user:{id,email,name,role,approved}}` + 세션 쿠키 |
| POST `/api/auth/login` | `{email,password}` | 위와 같음 |
| GET `/api/auth/me` | 세션 쿠키 | `{user:...}` 또는 401 |
| POST `/api/auth/logout` | 세션 쿠키 | `{ok:true}` |

비밀번호: 10~128자. 판매자는 관리자 승인 전 제작 API 사용 불가.

## 상품

`GET /api/products`

```json
{
  "products": [{
    "id":"prd_id", "name":"코튼 티셔츠", "brand":"판매자 상호", "category":"상의",
    "price":39000, "stock":10, "colors":["화이트"], "sizes":["S","M"],
    "image":"/api/products/prd_id/images/0",
    "images":["/api/products/prd_id/images/0"],
    "material":"면 100%", "origin":"대한민국", "description":"상품 설명",
    "createdAt":"2026-09-20T00:00:00+00:00", "sample":false
  }]
}
```

`stock`은 현재 각 색상×사이즈 조합에 동일하게 적용되는 재고 상한입니다. 실결제 전 SKU 재고 모델을 확장하세요.
공개 게시 상품의 이미지는 누구나 접근할 수 있습니다. 미게시 제작 이미지는 소유자 로그인 필요.

## AI 제작

`POST /api/generate` — multipart/form-data

| 필드 | 값 |
|---|---|
| front | 정면 원본 파일 |
| detail | 뒷면/디테일 원본 파일 |
| product | 아래 JSON 문자열 |
| plan | free 또는 paid |
| publishConsent | true 또는 false |

```json
{"name":"코튼 티셔츠","category":"상의","material":"면 100%","sizes":"S, M","colors":"화이트","origin":"대한민국","notes":"상품 특징"}
```

무료는 `publishConsent=true`, 독점은 관리자 부여 유료 권한이 필요합니다.

초기 응답 HTTP 202:

```json
{"jobId":"job_id","status":"queued","message":"제작 요청이 접수됐습니다."}
```

`GET /api/jobs` — 해당 판매자의 제작 내역 목록, 최대 최근 100건.

```json
{"jobs":[{"jobId":"job_id","name":"상품명","createdAt":"...","status":"processing"}]}
```

`GET /api/jobs/job_id` — 비동기 상태 확인.

진행 중: `{jobId,status:"queued" 또는 "processing",message}`
실패: `{jobId,status:"failed",error:{message}}`
완료:

```json
{
  "jobId":"job_id", "status":"completed", "plan":"free",
  "product":{"name":"코튼 티셔츠","category":"상의","material":"면 100%","sizes":"S, M","colors":"화이트","origin":"대한민국","notes":""},
  "description":"AI 설명",
  "visibleFeatures":["관찰된 특징"], "needsConfirmation":["확인 필요 항목"],
  "images":[{"url":"/api/jobs/job_id/images/0","alt":"상품 정면","kind":"main"}],
  "downloadAllowed":true, "downloadsRemaining":1,
  "imageGenerated":true, "mock":false
}
```

독점의 downloadsRemaining은 null(제한 없음). 유료 권한은 다운로드 시 다시 확인합니다.
`imageGenerated=false`면 새 AI 이미지 없이 원본을 사용한 결과입니다.
`mock=true`는 실제 AI 호출 없는 서버 테스트 결과입니다.

`POST /api/jobs/job_id/download` — 본문 없음, 성공 시 `text/html` 다운로드 파일 반환.
HTML에는 이미지 바이트를 내장합니다. 로그인·소유권·유료 권한·무료 횟수는 서버에서 검증합니다.

`POST /api/jobs/job_id/publish`

```json
{"price":39000,"stock":10,"reviewed":true}
```

무료·게시 동의·검토 완료 결과만 게시합니다. `{product: 상품객체}`를 반환합니다.
같은 jobId로 재요청하면 기존 상품을 반환합니다. 판매가 수정 API는 별도 구현 대상입니다.

## 주문 UI와 결제 연결점

`POST /api/checkout/quote`

```json
{"items":[{"id":"prd_id","color":"화이트","size":"M","quantity":2}]}
```

서버가 저장된 금액과 재고를 기준으로 계산합니다. 클라이언트 가격을 신뢰하지 않습니다.

```json
{"quoteId":"quote_id","subtotal":78000,"shipping":3000,"total":81000,"checkoutEnabled":false}
```

현재 배송비 3,000원은 참조 구현 값입니다. 실제 셀러별 정책으로 변경하세요.

**현재 POST `/api/orders`는 503이고 GET `/api/orders`는 빈 배열을 반환합니다.**
다음은 PG 연결 시 프런트가 기대하는 계약입니다. 현재 구현된 결제 API라는 뜻이 아닙니다.

```text
POST /api/orders
Idempotency-Key: 주문시도_UUID
{
  quoteId,
  shippingAddress:{recipient,phone,postalCode,address,addressDetail,deliveryNote,agree}
}
```

반환:

```json
{"order":{"id":"ord_id","status":"pending_payment","createdAt":"...","items":[{"name":"상품명","color":"화이트","size":"M","quantity":2,"price":39000}],"shipping":3000,"total":81000,"paymentUrl":"https://결제제공자/결제주소"}}
```

PG 연동 시 반드시 서버에서 견적 만료·소유권·재고 재검증, 원자적 재고 예약,
동일 idempotency key 재요청 처리, 결제 웹훅 서명 검증 및 중복 이벤트 처리를 구현하세요.
프런트 콜백이나 URL 파라미터만 보고 결제 완료로 바꾸면 안 됩니다.

## 오류

오류는 다음 모양의 JSON을 반환합니다.

```json
{"error":{"message":"사용자에게 표시할 오류"}}
```

401 로그인 필요 / 402 유료 권한 필요 / 403 권한·출처·횟수 / 409 상태 충돌 /
413 용량 초과 / 422 입력 오류 / 429 한도 / 503 설정 또는 기능 미연동.
