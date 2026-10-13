FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV MNIP_CONFIG_PATH=/mnip-config/config.yaml

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY config/config.example.yaml /app/config.example.yaml


COPY docker/entrypoint.sh /usr/local/bin/mnip-entrypoint
RUN chmod +x /usr/local/bin/mnip-entrypoint

ENTRYPOINT ["/usr/local/bin/mnip-entrypoint"]
