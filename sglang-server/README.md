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

# 以glm5.1为例子
bash docker_run.sh config/glm51/regular/pp8-fp8kv-deploy.env
```

### PD router节点启动

```bash
#以glm5.1为例
bash docker_run.sh config/glm51/prefill/cp8ep8-fp8kv-deploy.env
bash docker_run.sh config/glm51/decode/dp8ep8-fp8kv-deploy.env
# 需要根据实际工作节点服务的url修改脚本里的urls
bash router_run.sh
```
