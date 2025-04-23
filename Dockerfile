FROM python:3.10-slim

# 필수 패키지 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 모든 파일 복사
COPY . /app
WORKDIR /app

# 외부 접속 허용
EXPOSE 9000
CMD ["streamlit", "run", "app.py", "--server.port=9000", "--server.address=0.0.0.0"]
