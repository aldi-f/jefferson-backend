FROM python:3.13-trixie
LABEL org.opencontainers.image.source=https://github.com/aldi-f/gelato

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

CMD ["python","-m","app.main"]
