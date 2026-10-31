FROM pytorch/pytorch:2.9.0-cuda13.0-cudnn9-devel

# 要安裝哪一組 custom node，對應 profiles/<PROFILE>.yaml
ARG PROFILE=default

# 合併所有系統套件安裝和清理動作
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    build-essential \
    fontconfig \
    fonts-freefont-ttf \
    pkg-config \
    libcairo2-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone ComfyUI 主程式
RUN git clone --depth 1 https://github.com/Comfy-Org/ComfyUI.git

# 安裝 ComfyUI 基礎依賴
RUN pip install --no-cache-dir -r /app/ComfyUI/requirements.txt

# 依 profile 安裝 custom node（名稱與 repo 對照見 nodes.yaml）
COPY nodes.yaml install_custom_nodes.py /app/
COPY profiles/ /app/profiles/
RUN python /app/install_custom_nodes.py ${PROFILE} && \
    rm -rf /app/nodes.yaml /app/install_custom_nodes.py /app/profiles

EXPOSE 8188
WORKDIR /app/ComfyUI

CMD ["bash"]