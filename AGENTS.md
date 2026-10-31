# comfyui-deploy

以 Docker（GPU）佈署 ComfyUI。Agent 如何操作容器內的 ComfyUI 屬於 `comfyui-agent`，不在此處理。

- 容器：`docker-compose.yml` 每個 profile 一個 service（`comfyui` 建置 `comfyui:latest`），共用 port 8188 與 GPU，同一時間只啟動一個。
- Profile：`profiles/<name>.yaml` 列出該 workflow 要裝的 node（可附 `source`、`tasks` 備註）。`nodes.yaml` 是 node 名稱到 git repo 的唯一對照；`install_custom_nodes.py` 依 profile build 進 image。新增 node：在 `nodes.yaml` 加一筆，再加進 profile，重新 build。新增 profile：加 `profiles/<name>.yaml` 與對應的 compose service。
- `custom_nodes` 不掛載到 host：node 依賴常互相衝突，烘進 profile image 才不留殘渣。
- Host 目錄 `/data/comfyui/{models,input,output,workflows}` 掛進容器，是模型與輸出的 source of truth。
- `docs/gguf.md`：GGUF 轉換與量化流程，處理 GGUF 模型時先讀。
