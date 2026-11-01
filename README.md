# comfyui-deploy：Profile 驅動的 Docker 化 ComfyUI 部署環境

以 Docker（NVIDIA GPU）部署乾淨、可重現的 **ComfyUI** 執行環境。

傳統 ComfyUI 把所有 `custom_nodes` 裝在同一環境，不同節點的 Python 依賴經常互相衝突。本專案透過 **Profile 機制**（`nodes.yaml` + `profiles/*.yaml`）在建置 Docker Image 時決定要預載哪些 Custom Nodes：
- **`custom_nodes` 烘進 Image，不掛載到 Host**：切換 Profile 不留依賴殘渣，Docker Layer Cache 共用 `base` 基底層。
- **模型與產出持久化於 Host**：`/data/comfyui/{models,input,output,workflows}` 掛載進容器，作為唯一的資料來源。

---

## 1. 系統需求

- Linux `x86_64`
- NVIDIA GPU + NVIDIA Driver
- Docker & [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- Host 預留模型與輸出目錄：`/data/comfyui/{models,input,output,workflows}`

---

## 2. 內建 Profiles 一覽

所有 Profile 皆繼承自 [`profiles/base.yaml`](profiles/base.yaml)（內建 `ComfyUI-Manager`、`ComfyUI-Lora-Manager`、`ComfyUI-GGUF`、`rgthree-comfy`）：

| Profile 名稱 | 啟動指令 | 預載額外 Custom Nodes | 適用場景與搭配專案 |
| --- | --- | --- | --- |
| **`default`** | `docker compose up -d --build` | *(僅 `base` 基底節點)* | 輕量文生圖（SDXL / Illustrious / Flux 原生節點）、LoRA 驗證 |
| **`pose-gallery`** | `PROFILE=pose-gallery docker compose up -d --build` | `comfyui_controlnet_aux`（含 `DepthAnythingV2Preprocessor`） | 搭配 [kime541200/ai-pose-gallery-zh](https://github.com/kime541200/ai-pose-gallery-zh) 與 [kime541200/ai-pose-gallery-mcp](https://github.com/kime541200/ai-pose-gallery-mcp) 執行 **FLUX 3 Image Klein / Qwen-Image-Edit 多圖角色合成**（3D 深度姿勢控制） |
| **`general`** | `PROFILE=general docker compose up -d --build` | `ControlAltAI-Nodes`、`ComfyUI-KJNodes`、`ComfyUI-Inpaint-CropAndStitch`、`efficiency-nodes-comfyui` | 通用進階圖像控制與局部重繪（Inpaint） |
| **`wan-smooth`** | `PROFILE=wan-smooth docker compose up -d --build` | `ComfyUI-WanVideoWrapper`、`ComfyUI-VideoHelperSuite`、`ComfyUI-MMAudio`、`ComfyUI-VFI` 等 11 個節點 | Wan 2.2 圖生影片（I2V）／文生影片（T2V）／首尾幀與音效生成 |

> 詳細的 Profile 繼承機制與新增 Custom Node 方式請見 [`docs/profiles.md`](docs/profiles.md)；GGUF 模型轉換與量化說明請見 [`docs/gguf.md`](docs/gguf.md)。

---

## 3. 快速啟動與常用操作

```bash
# 1. 啟動預設 Profile（或指定 PROFILE=pose-gallery）
PROFILE=pose-gallery docker compose up -d --build

# 2. 查看容器內已安裝的 Custom Nodes
docker exec comfyui ls /app/ComfyUI/custom_nodes

# 3. 檢查 ComfyUI API 健康狀態（預期回傳 200）
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8188/system_stats

# 4. 切換至其他 Profile 前先停止現有容器（共用 Port 8188 與 GPU）
docker compose down --remove-orphans
PROFILE=wan-smooth docker compose up -d --build
```

---

## 4. 搭配 `pose-gallery` Profile 準備多圖角色合成模型

若啟動 `PROFILE=pose-gallery` 搭配 [kime541200/ai-pose-gallery-zh](https://github.com/kime541200/ai-pose-gallery-zh)（AI 角色合成台）或 [kime541200/ai-pose-gallery-mcp](https://github.com/kime541200/ai-pose-gallery-mcp)，可執行以下指令將預設推薦的 **FLUX 3 Image Klein Distilled (Int8)** 模型（共 3 個檔案，約 10.27 GB，免 Hugging Face Token）下載至 `/data/comfyui/models`：

```bash
COMFYUI_MODELS_DIR=${COMFYUI_MODELS_DIR:-/data/comfyui/models}
mkdir -p "$COMFYUI_MODELS_DIR"/{diffusion_models,text_encoders,vae}

wget -c -O "$COMFYUI_MODELS_DIR/diffusion_models/flux3-image-klein-int8-convrot.safetensors" \
  "https://huggingface.co/ml-resources/flux-3-image-klein-comfy/resolve/main/diffusion_models/flux3-image-klein-int8-convrot.safetensors"

wget -c -O "$COMFYUI_MODELS_DIR/text_encoders/qwen3vl_4b_int8_convrot.safetensors" \
  "https://huggingface.co/ml-resources/flux-3-image-klein-comfy/resolve/main/text_encoders/qwen3vl_4b_int8_convrot.safetensors"

wget -c -O "$COMFYUI_MODELS_DIR/vae/flux2-vae.safetensors" \
  "https://huggingface.co/Comfy-Org/flux2-dev/resolve/main/split_files/vae/flux2-vae.safetensors"
```

---

## 5. 相關開源生態系（Ecosystem）

本專案可獨立作為地端 ComfyUI 伺服器，也可與以下開源專案串接成完整的地端生圖與 AI Agent 工作流，歡迎提交 Issue / PR 共同新增 Profile 或優化配置：

| 專案 Repo | 角色與功能說明 |
| --- | --- |
| **[kime541200/ai-pose-gallery-zh](https://github.com/kime541200/ai-pose-gallery-zh)** | **AI 角色參考圖庫與合成台（4,345 張全中文索引）**：提供姿勢、服裝、人像參考圖庫與 `/studio` Web 合成台，直連本容器執行 `FLUX 3 Image Klein` 或 `Qwen-Image-Edit-2509` 多圖角色合成。 |
| **[kime541200/ai-pose-gallery-mcp](https://github.com/kime541200/ai-pose-gallery-mcp)** | **圖庫檢索與多圖合成 MCP Server**：讓 Coding Agent 用自然語言檢索參考圖並自動呼叫本 ComfyUI 容器合成角色圖。 |
| **[kime541200/comfy-mcp](https://github.com/kime541200/comfy-mcp)** | **ComfyUI 管理與執行 MCP Server**：Docker 化 Streamable HTTP MCP，提供節點探索、Workflow 驗證與模型下載。 |
| **[kime541200/comfyui-agent](https://github.com/kime541200/comfyui-agent)** | **AI Agent 生圖工作區**：內建已驗證的 API 工作流模板庫、MCP 設定範本與 Agent 操作規範。 |
| **[kime541200/lora-training](https://github.com/kime541200/lora-training)** | **Docker 化 LoRA 訓練工具**：以 kohya `sd-scripts` 訓練角色 LoRA，產出的 `.safetensors` 可直接放入 `/data/comfyui/models/loras` 載入生圖。 |
