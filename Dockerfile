FROM python:3.12-slim

LABEL maintainer="nesquena"
LABEL description="Hermes Web UI — browser interface for Hermes Agent"

WORKDIR /app

# Copy source
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run as non-root user
RUN groupadd -r webui && useradd -r -g webui -d /data -s /bin/bash webui && \
    mkdir -p /data && chown -R webui:webui /data /app

# Default to binding all interfaces (required for container networking)
ENV HERMES_WEBUI_HOST=0.0.0.0
ENV HERMES_WEBUI_PORT=8787

# State directory (mount as volume for persistence)
ENV HERMES_WEBUI_STATE_DIR=/data

EXPOSE 8787
USER webui

CMD ["python", "server.py"]
