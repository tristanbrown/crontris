# Build image
FROM python:3.8-slim as builder
COPY requirements.txt /app/requirements.txt
WORKDIR app
RUN pip install --user -r requirements.txt
COPY ./src /app

# Production image
FROM python:3.8-slim as crontris
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app
WORKDIR app
ENV PATH=/root/.local/bin:$PATH
ENTRYPOINT ["python", "-m", "crontris"]