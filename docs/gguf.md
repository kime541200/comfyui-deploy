> 官方流程參考 [ComfyUI-GGUF/tools](https://github.com/city96/ComfyUI-GGUF/tree/main/tools)（2025-08 最後更新；與官方比對於 2026-10-18）

1. Install

必須先裝好 [ComfyUI-GGUF](https://github.com/city96/ComfyUI-GGUF.git) custom node。

> 已在建置Docker Image時裝好了（`nodes.yaml` 與 `profiles/*.yaml`）

2. 安裝好GGUF套件（需要 `gguf>=0.13.0`）

```bash
pip install "gguf>=0.13.0"
```


3. 將模型轉成GGUF格式

在Container中，使用以下指令進行轉換
```bash
cd /app/ComfyUI/custom_nodes/ComfyUI-GGUF/tools

python convert.py \
--src /app/ComfyUI/models/unet/ostris/Flex.1-alpha/Flex.1-alpha.safetensors
```

> 轉換時沒有使用 `--dst` 指定輸出路徑的話會輸出在原始模型目錄下

注意（官方新增）：

- Flux 不要用 diffusers UNET 格式（q/k/v 被合併成 qkv 會失敗）。用預設/reference checkpoint key 格式；可在 ComfyUI 載入後用內建 `ModelSave` node 轉換。
- HunyuanVideo / Wan 2.1 轉換時會出現 5D tensor 警告：此時輸出的是**無法使用**的中間檔，只能拿去量化，建議放在獨立的 `raw` 資料夾。量化後必須手動執行 `fix_5d_tensors.py` 補回缺失的 key。

4. 量化模型

量化需要**打過補丁**的 llama.cpp（官方 `lcpp.patch` 加入圖像模型支援），不是一般的 llama.cpp。目前 image 內沒有 `/app/llama.cpp`，需要先自行編譯：

```bash
cd /app/ComfyUI/custom_nodes/ComfyUI-GGUF/tools

python fix_lines_ending.py   # 若 patch 檔是 CRLF 才需要
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
git checkout tags/b3962
git apply ../lcpp.patch
cmake -B build
cmake --build build --config Release -j"$(nproc)" --target llama-quantize
```

編譯完成後量化，例如：
```bash
./build/bin/llama-quantize \
/app/ComfyUI/models/unet/ostris/Flex.1-alpha/Flex.1-alpha-BF16.gguf \
/app/ComfyUI/models/unet/ostris/Flex.1-alpha/Flex.1-alpha-q4-K-M.gguf \
Q4_K_M
```

> 容器內編譯的 `llama.cpp` 在容器重建後會消失；可考慮把編譯步驟寫進 Dockerfile 或改成一次性 builder 容器。
> 編譯需要 `cmake`，目前 image 內是否有，尚未確認（有 `build-essential`）。