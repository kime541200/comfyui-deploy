# Profile：決定 image 內有哪些 custom node

預設 image 只含 `base` 的 node；不同 workflow 需要的 node 各自成一個 profile，build 時用 `PROFILE` 選擇。

## 結構

| 檔案 | 內容 |
| --- | --- |
| `nodes.yaml` | node 名稱 → git repo，唯一對照表 |
| `profiles/base.yaml` | 所有 profile 共用的最小集合（Manager、Lora-Manager、GGUF、rgthree） |
| `profiles/<name>.yaml` | `extends: base` 加上該 workflow 專屬的 `nodes`；可選 `source`、`tasks` 備註 |

`extends` 先展開再合併、去重；`default` 只有 base。

## 使用

```bash
docker compose up -d --build                      # default（只有 base）
PROFILE=general docker compose up -d --build      # 其他 profile
docker compose down                               # 切換前先停止，共用 port 8188 與 GPU
```

image 標籤為 `comfyui:<PROFILE>`；Dockerfile 把 base 獨立成一層，切換 profile 時共用其快取。

## 新增

- 新 node：在 `nodes.yaml` 加一筆，再加進要用的 profile。
- 新 profile：加 `profiles/<name>.yaml`（`extends: base`），不必改 compose。
- 加完先驗證名稱：`python install_custom_nodes.py --dry-run <name>`，再 build。
- 只有幾乎所有 workflow 都用到的 node 才放進 `base`；其餘放 profile，避免依賴互相衝突。
