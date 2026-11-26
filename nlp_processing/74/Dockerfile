FROM ghcr.io/astral-sh/uv:0.9.21 AS uv
FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    adwaita-icon-theme dbus-x11 fonts-dejavu-core openbox thunar wmctrl x11vnc xauth xdotool xvfb \
    && rm -rf /var/lib/apt/lists/*
ADD https://codeload.github.com/novnc/noVNC/tar.gz/refs/tags/v1.6.0 /tmp/novnc.tar.gz
RUN echo '5066103959ef4e9b10f37e5a148627360dd8414e4cf8a7db92bdbd022e728aaa  /tmp/novnc.tar.gz' | sha256sum -c - \
    && mkdir -p /opt/novnc \
    && tar -xzf /tmp/novnc.tar.gz --strip-components=1 -C /opt/novnc \
    && rm /tmp/novnc.tar.gz
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked
RUN useradd --create-home computeruse
COPY run.py ./
USER computeruse
ENTRYPOINT ["xvfb-run", "-a", "-s", "-screen 0 1024x768x24", "/app/.venv/bin/python", "run.py"]
