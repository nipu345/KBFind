FROM python:3.12-slim

# Lambda Web Adapter runs as a Lambda extension and forwards invocations to the
# HTTP server on $PORT. Outside Lambda it does nothing, so this exact image also
# runs locally with a plain `docker run -p 8080:8080`.
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.9.1 /lambda-adapter /opt/extensions/lambda-adapter

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /var/task

COPY requirements.txt .
RUN pip install -r requirements.txt

# Bake the embedding model into the image. Lambda's filesystem is read-only
# outside /tmp, and downloading the model on every cold start would be slow.
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('BAAI/bge-small-en-v1.5', cache_dir='/opt/models')"

COPY app ./app
COPY kb ./kb

ENV PORT=8080 \
    AWS_LWA_READINESS_CHECK_PATH=/health \
    MODEL_CACHE_DIR=/opt/models \
    MODEL_OFFLINE=1 \
    HF_HOME=/tmp/hf \
    INDEX_PATH=/tmp/index.json

EXPOSE 8080
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
