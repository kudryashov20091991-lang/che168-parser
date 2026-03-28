FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY che168_github_action.py .

CMD ["python", "che168_github_action.py"]
