# SGLang部署LLM模型的最佳实践

## 模型列表

- deepseek-v32
- glm5.1

## 工作节点类型

- prefill: PD分离部署的Prefill节点。
- decode: PD分离部署的Decode节点。
- regular: 非PD分离部署。

## 部署方式

### 工作节点启动

```bash
bash docker_run.sh deploy_env_path
```

### PD router节点启动

```bash
# 需要根据实际工作节点服务的url修改脚本里的urls
bash router_run.sh
```
