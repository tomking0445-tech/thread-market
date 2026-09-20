# 배포 담당자에게 그대로 전달할 내용

아래 내용을 이 폴더 전체와 함께 전달하세요. 실제 API 키는 메시지에 포함하지 마세요.

---

이 프로젝트는 THREAD MARKET 쇼핑몰입니다. Python 3.12 + FastAPI 백엔드와 public/index.html 프런트가 포함되어 있습니다.

1. README.md와 API.md를 먼저 확인해 주세요.
2. 이 폴더를 GitHub 저장소 루트에 올리고 Railway에 연결해 주세요.
3. Dockerfile을 사용하며 uvicorn은 worker 1개, Railway는 replica 1개로 운영해 주세요.
4. Railway Volume을 /data에 마운트하고 DATA_DIR=/data를 설정해 주세요.
5. OPENAI_API_KEY는 Railway Variables의 비밀 환경 변수에만 넣어 주세요. 코드/GitHub/채팅에 기록하지 마세요.
6. 공개 도메인을 생성하고 ALLOWED_ORIGINS에 그 https Origin을 정확하게 등록해 주세요.
7. COOKIE_SECURE=true, COOKIE_SAMESITE=lax를 적용해 주세요.
8. 처음에는 GENERATION_MODE=mock으로 가입→판매자 승인→업로드→결과→다운로드→게시를 확인한 뒤 ai로 변경해 주세요.
9. 실제 서버에서 python admin.py approve-seller 가입한이메일 을 실행해 판매자 권한을 승인해 주세요.
10. /api/health와 /에서 각각 서버 상태와 쇼핑몰을 확인해 주세요.
11. 배포 브랜치 push 시 자동배포되도록 연결해 주세요.
12. 실제 PG 결제/배송/정산은 아직 미연동입니다. CHECKOUT_ENABLED 값만 변경해 실제 주문을 받지 마세요.
13. 운영 전 사업자 정보·약관·개인정보·반품/배송 정책을 등록해 주세요.
14. 외부 프런트를 쓰면 CONFIG.mode='api', CONFIG.apiBase=백엔드주소로 변경하고 CORS/쿠키도 함께 검증해 주세요.
15. 배포 결과 URL, 적용한 환경 변수 이름(값 제외), Volume 백업 계획, 남은 연동 항목을 전달해 주세요.

이미 비밀키를 외부 채팅에 붙여 넣었다면, 운영에는 새로 발급한 키를 사용하고 노출된 키를 폐기해 주세요.
