# comfyui-deploy

以 Docker（GPU）佈署 ComfyUI。Agent 如何操作容器內的 ComfyUI 屬於 [kime541200/comfyui-agent](https://github.com/kime541200/comfyui-agent)，不在此處理。

- 容器：`docker-compose.yml` 單一 service，以 `PROFILE` 選擇要建置的 profile，同一時間只啟動一個（共用 port 8188 與 GPU）。
- Profile 與 node 管理（`nodes.yaml`、`profiles/`、base 的取捨）：新增或調整 node 前先讀 `docs/profiles.md`。
- `custom_nodes` 不掛載到 host：node 依賴常互相衝突，烘進 profile image 才不留殘渣。
- Host 目錄 `/data/comfyui/{models,input,output,workflows}` 掛進容器，是模型與輸出的 source of truth。
- `docs/gguf.md`：GGUF 轉換與量化流程，處理 GGUF 模型時先讀。
