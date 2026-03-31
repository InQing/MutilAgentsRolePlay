# Ubuntu Docker 部署说明

## 1. 适用场景

本说明用于 Ubuntu 云服务器上的常驻部署。

当前 Docker Compose 已包含：

- `web`：Next.js 前端
- `api`：FastAPI 后端
- `postgres`：主数据库
- `redis`：缓存与后续调度协作层

部署后，外部主要访问 `web` 服务；`api` 仅绑定到服务器本机回环地址，`postgres` 和 `redis` 不对公网开放。

## 2. 服务器准备

需要先准备：

- Ubuntu 22.04 或更新版本
- Docker Engine 或 Docker Desktop for Linux
- Docker Compose Plugin
- 已开放服务器防火墙端口：`80`

建议验证：

```bash
docker --version
docker compose version
```

## 3. 项目配置

在仓库根目录执行：

```bash
cp .env.example .env
```

默认配置含义：

- `WEB_PORT=80`：前端对外暴露端口
- `API_PORT=8000`：API 仅绑定到服务器本机 `127.0.0.1`
- `MARP_DATABASE_URL`：API 通过 Compose 内部网络连接 PostgreSQL
- `MARP_REDIS_URL`：API 通过 Compose 内部网络连接 Redis

如果服务器上 `80` 已被其他服务占用，可以把 `.env` 中的 `WEB_PORT` 改成别的端口。

## 4. 启动方式

首次部署或镜像更新后执行：

```bash
docker compose up -d --build
```

如果镜像构建阶段需要走代理，请在 `.env` 中设置 `BUILD_HTTP_PROXY` / `BUILD_HTTPS_PROXY`。如果代理运行在宿主机本机，请写成 `http://host.docker.internal:7890`，不要写 `127.0.0.1`，因为构建容器里的 `127.0.0.1` 指向的是容器自己。

查看状态：

```bash
docker compose ps
docker compose logs api
docker compose logs web
```

## 5. 访问方式

部署成功后，默认访问：

- `http://<server-ip>/`
- `http://<server-ip>/chat`
- `http://<server-ip>/moments`
- `http://<server-ip>/director`

如果需要在服务器本机检查 API，可用：

- `http://127.0.0.1:8000/api/health`
- `http://127.0.0.1:8000/api/world/state`

## 6. 当前注意事项

- 当前部署默认是 HTTP，没有内置 HTTPS
- 如果要正式对公网开放，建议再加 Nginx / Caddy 反向代理与 TLS
- Redis 目前还未进入完整调度协作链路，但容器已保留
- PostgreSQL / Redis 的公网端口默认不开放
