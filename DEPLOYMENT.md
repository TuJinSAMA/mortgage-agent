# 部署文档

本文档说明如何配置 GitHub Actions 自动部署流水线。

## 部署架构

本项目使用 GitHub Actions 实现 CI/CD 自动部署：

1. 当代码推送到 `main` 分支时，自动触发部署流程
2. GitHub Actions 通过 SSH 连接到远程服务器
3. 在服务器上拉取最新代码
4. 使用 Docker Compose 构建并运行应用

## 前置要求

### 1. 服务器准备

确保你的服务器已安装：
- Docker
- Docker Compose
- Git

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 安装 Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# 验证安装
docker --version
docker compose version
```

### 2. 服务器上克隆项目

```bash
cd /root
git clone <your-repository-url> mortgage-agent
cd mortgage-agent
```

### 3. 配置环境变量

在服务器上创建 `.env` 文件：

```bash
cd /root/mortgage-agent
cp .env.example .env
nano .env
```

编辑 `.env` 文件，填入你的实际配置：

```env
OPENAI_API_KEY=sk-your-actual-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4
```

## 配置 GitHub Secrets

在 GitHub 仓库中配置以下 Secrets：

### 步骤：

1. 进入你的 GitHub 仓库
2. 点击 **Settings** > **Secrets and variables** > **Actions**
3. 点击 **New repository secret** 添加以下密钥：

### 需要配置的 Secrets：

| Secret 名称 | 说明 | 示例值 |
|------------|------|--------|
| `SERVER_HOST` | 服务器 IP 地址或域名 | `123.45.67.89` 或 `example.com` |
| `SERVER_USER` | SSH 登录用户名 | `root` |
| `SERVER_SSH_KEY` | SSH 私钥（完整内容） | 见下方说明 |
| `SERVER_PORT` | SSH 端口（可选，默认 22） | `22` |

### 生成 SSH 密钥对

如果你还没有 SSH 密钥，可以在本地生成：

```bash
# 生成新的 SSH 密钥对
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_actions_deploy

# 查看公钥（需要添加到服务器）
cat ~/.ssh/github_actions_deploy.pub

# 查看私钥（需要添加到 GitHub Secrets）
cat ~/.ssh/github_actions_deploy
```

### 将公钥添加到服务器

```bash
# 在服务器上执行
mkdir -p ~/.ssh
nano ~/.ssh/authorized_keys

# 将公钥内容粘贴到文件中，保存退出
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### 将私钥添加到 GitHub Secrets

1. 复制整个私钥内容（包括 `-----BEGIN OPENSSH PRIVATE KEY-----` 和 `-----END OPENSSH PRIVATE KEY-----`）
2. 在 GitHub Secrets 中创建 `SERVER_SSH_KEY`，粘贴私钥内容

## 部署流程

### 自动部署

推送代码到 `main` 分支时自动触发：

```bash
git add .
git commit -m "feat: 新功能"
git push origin main
```

### 手动部署

1. 进入 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择 **Deploy to Production** workflow
4. 点击 **Run workflow** 按钮
5. 选择分支并确认运行

## 查看部署状态

### 在 GitHub 上查看

1. 进入 **Actions** 标签
2. 查看最新的 workflow 运行记录
3. 点击查看详细日志

### 在服务器上查看

```bash
# 查看容器状态
cd /root/mortgage-agent
docker-compose ps

# 查看应用日志
docker-compose logs -f mortgage-agent

# 查看最近 100 行日志
docker-compose logs --tail=100 mortgage-agent

# 测试健康检查（应用运行在 8888 端口）
curl http://localhost:8888/health
```

## 常见问题

### 1. SSH 连接失败

**问题**：GitHub Actions 无法连接到服务器

**解决方案**：
- 检查 `SERVER_HOST` 和 `SERVER_PORT` 是否正确
- 确认服务器防火墙允许 SSH 连接
- 验证 SSH 密钥是否正确配置

```bash
# 在服务器上检查 SSH 配置
sudo nano /etc/ssh/sshd_config

# 确保以下配置启用：
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys

# 重启 SSH 服务
sudo systemctl restart sshd
```

### 2. Docker 构建失败

**问题**：容器构建或启动失败

**解决方案**：
```bash
# 查看详细错误日志
docker-compose logs

# 手动构建测试
docker-compose build --no-cache

# 清理并重新构建
docker-compose down -v
docker system prune -f
docker-compose up -d --build
```

### 3. 环境变量未生效

**问题**：应用无法读取环境变量

**解决方案**：
- 确认服务器上 `/root/mortgage-agent/.env` 文件存在且配置正确
- 检查 `.env` 文件权限：`chmod 600 .env`
- 重启容器：`docker-compose restart`

### 4. 端口冲突

**问题**：端口已被占用

**解决方案**：

本项目默认使用 **8888 端口**（避免与 Nginx 等常见服务冲突）。

如果 8888 端口也被占用：
```bash
# 查看端口占用
sudo lsof -i :8888

# 修改 docker-compose.yml 中的端口映射
# 将 "8888:8000" 改为 "其他端口:8000"
# 例如：- "9000:8000"
```

## 回滚部署

如果新版本有问题，可以快速回滚：

```bash
# SSH 登录到服务器
ssh root@your-server-ip

# 进入项目目录
cd /root/mortgage-agent

# 回滚到上一个版本
git log --oneline  # 查看提交历史
git reset --hard <commit-hash>  # 回滚到指定提交

# 重新部署
docker-compose down
docker-compose up -d --build
```

## 监控和维护

### 定期清理 Docker 资源

```bash
# 清理未使用的镜像
docker image prune -a -f

# 清理未使用的容器
docker container prune -f

# 清理未使用的卷
docker volume prune -f

# 查看磁盘使用情况
docker system df
```

### 日志管理

Docker Compose 配置了日志轮转（最多 3 个文件，每个最大 10MB），无需手动清理。

如需查看日志文件位置：
```bash
docker inspect mortgage-agent | grep LogPath
```

## 安全建议

1. **定期更新依赖**：定期更新 Python 包和 Docker 镜像
2. **限制 SSH 访问**：配置防火墙只允许必要的 IP 访问
3. **使用强密码**：为服务器和数据库使用强密码
4. **定期备份**：定期备份数据和配置文件
5. **监控日志**：定期检查应用和系统日志

## 性能优化

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 配置 HTTPS

```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取 SSL 证书
sudo certbot --nginx -d your-domain.com
```

## 联系支持

如有问题，请：
1. 查看 GitHub Actions 日志
2. 查看服务器上的应用日志
3. 提交 GitHub Issue

