🧬 자가진단표 실행 안내

1. 실행 방법
────────────────────────────
# 가상환경 진입 후 아래 명령어 실행
streamlit run app.py

2. 구성 파일 설명
────────────────────────────
- app.py                 👉 메인 앱 파일
- config_options.json    👉 선택 옵션(지역/이메일/사육단계) 설정
- /data/                 👉 증상/소견/항생제 CSV + 샘플 이미지
- /fonts/                👉 PDF용 한글 폰트 (CJONLYONENEWbodyRegular.ttf)
- requirements.txt       👉 필요한 Python 라이브러리 목록

3. 주요 기능
────────────────────────────
- 증상, 해부학, 항생제 데이터 체크
- 상단 입력값 + 선택 항목을 PDF로 저장 (한글 지원)

4. 기타
────────────────────────────
- PDF 저장 시 특수기호(📅 → - 등)로 대체되어 출력됨
- Streamlit UI에서는 이모지 유지됨
# streamlit_cj
# streamlit_cj
