# 快速开始

## 🚀 应用访问

应用部署后运行在 **8888 端口**：

```bash
# 健康检查
curl http://your-server-ip:8888/health

# 或使用域名
curl http://your-domain.com:8888/health
```

## 📡 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/chat` | POST | 对话接口 |
| `/check-missing-fields` | POST | 检查缺失字段 |
| `/loan-products` | POST | 获取贷款产品 |

### 示例请求

```bash
# 健康检查
curl http://localhost:8888/health

# 对话接口
curl -X POST http://localhost:8888/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "什么是 FHA 贷款？"}'

# 获取贷款产品
curl -X POST http://localhost:8888/loan-products \
  -H "Content-Type: application/json" \
  -d '{
    "creditScore": [700, 800],
    "loanTerm": 30,
    "armOrFixed": "fix"
  }'
```

## 🔧 常用命令

### 查看日志
```bash
cd /root/mortgage-agent
docker-compose logs -f
```

### 重启应用
```bash
docker-compose restart
```

### 停止应用
```bash
docker-compose down
```

### 启动应用
```bash
docker-compose up -d
```

### 重新构建并启动
```bash
docker-compose up -d --build
```

### 查看容器状态
```bash
docker-compose ps
```

## 🌐 配置 Nginx 反向代理（可选）

如果你想通过 80/443 端口访问（不带端口号），可以配置 Nginx：

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

保存到 `/etc/nginx/sites-available/mortgage-agent`，然后：

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/mortgage-agent /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

配置后就可以直接访问：`http://your-domain.com/health`

## 🔒 配置 HTTPS（推荐）

```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取 SSL 证书
sudo certbot --nginx -d your-domain.com

# Certbot 会自动配置 HTTPS 并设置自动续期
```

配置后可以通过 HTTPS 访问：`https://your-domain.com/health`

## 📊 监控应用

### 查看资源使用
```bash
docker stats mortgage-agent
```

### 查看磁盘使用
```bash
docker system df
```

### 清理未使用的资源
```bash
docker system prune -f
```

## 🐛 故障排查

### 应用无法访问

1. 检查容器是否运行
```bash
docker-compose ps
```

2. 查看日志
```bash
docker-compose logs --tail=50
```

3. 检查端口是否监听
```bash
sudo netstat -tlnp | grep 8888
```

4. 检查防火墙
```bash
# 如果使用 ufw
sudo ufw allow 8888

# 如果使用 firewalld
sudo firewall-cmd --permanent --add-port=8888/tcp
sudo firewall-cmd --reload
```

### 环境变量未生效

检查 `.env` 文件：
```bash
cd /root/mortgage-agent
cat .env
```

确保包含：
```env
OPENAI_API_KEY=your_actual_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4
```

重启容器：
```bash
docker-compose restart
```

## 📞 获取帮助

- 查看完整部署文档：`DEPLOYMENT.md`
- 查看依赖管理文档：`UPDATE_DEPENDENCIES.md`
- 查看 API 使用文档：`API_USAGE.md`

