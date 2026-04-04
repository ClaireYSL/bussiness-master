ARG PYTHON_BASE_IMAGE=docker.1ms.run/python:3.11-slim
FROM ${PYTHON_BASE_IMAGE}

ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ARG PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_PROGRESS_BAR=off \
    PIP_INDEX_URL=${PIP_INDEX_URL} \
    PIP_TRUSTED_HOST=${PIP_TRUSTED_HOST} \
    LOCAL_KNOWLEDGE_DOCS_ROOT=/app/docs \
    APP_ROOT=/app

WORKDIR /app

RUN useradd --create-home --shell /usr/sbin/nologin appuser

COPY pyproject.toml README.md alembic.ini ./
COPY apps ./apps
COPY shared ./shared
COPY collectors ./collectors
COPY deliveries ./deliveries
COPY parsers ./parsers
COPY migrations ./migrations
COPY tools ./tools
COPY docs/L1客户案例/*.md ./docs/L1客户案例/
COPY docs/product_matrix_processed/*.md ./docs/product_matrix_processed/
COPY docs/用户调研报告.md ./docs/用户调研报告.md
COPY docs/vendor_client_db.csv ./docs/vendor_client_db.csv

RUN python -m pip install .

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--loop", "asyncio", "--http", "h11"]
