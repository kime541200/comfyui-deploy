# comfyui-deploy

以 Docker 佈署 ComfyUI，依 profile 決定烘進 image 的 custom node；預設只含最基本的 node（見 `docs/profiles.md`）。

需求：Linux x86_64、NVIDIA GPU、NVIDIA Container Toolkit。模型與輸出存於 host 的 `/data/comfyui/{models,input,output,workflows}`。

```bash
docker compose up -d --build                      # default：只含 base node
PROFILE=wan-smooth docker compose up -d --build   # 其他 profile（同時只啟動一個，先 docker compose down）
docker exec comfyui ls /app/ComfyUI/custom_nodes  # 查看已裝 node
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8188/system_stats   # 預期 200
```

若 8188 被佔用：`docker compose down --remove-orphans`。Agent 操作請見 [kime541200/comfyui-agent](https://github.com/kime541200/comfyui-agent)。
