# 依赖管理说明

本项目使用 **uv** 进行依赖管理，并通过 **requirements.txt** 在 Docker 中部署。

## 工作流程

```
开发环境 (uv)  →  导出  →  requirements.txt  →  Docker 部署 (pip)
```

## 为什么这样做？

| 工具 | 用途 | 优势 |
|------|------|------|
| **uv** | 本地开发 | 快速、依赖锁定、虚拟环境管理 |
| **requirements.txt** | Docker 部署 | 简单、快速、兼容性好 |

## 如何添加新依赖

### 1. 使用 uv 添加依赖

```bash
# 添加生产依赖
uv add fastapi

# 添加开发依赖
uv add --dev pytest

# 添加指定版本
uv add "pydantic>=2.0.0"
```

### 2. 导出 requirements.txt

```bash
# 导出生产依赖（不包含开发依赖和哈希值）
uv export --no-dev --no-hashes --no-emit-project -o requirements.txt
```

### 3. 提交更改

```bash
git add pyproject.toml uv.lock requirements.txt
git commit -m "feat: 添加新依赖"
git push
```

## 如何更新依赖

### 更新所有依赖到最新版本

```bash
# 更新所有依赖
uv lock --upgrade

# 导出新的 requirements.txt
uv export --no-dev --no-hashes --no-emit-project -o requirements.txt

# 提交更改
git add uv.lock requirements.txt
git commit -m "chore: 更新依赖"
git push
```

### 更新特定依赖

```bash
# 更新特定包
uv lock --upgrade-package fastapi

# 导出新的 requirements.txt
uv export --no-dev --no-hashes --no-emit-project -o requirements.txt

# 提交更改
git add uv.lock requirements.txt
git commit -m "chore: 更新 fastapi"
git push
```

## 如何移除依赖

```bash
# 移除依赖
uv remove package-name

# 导出新的 requirements.txt
uv export --no-dev --no-hashes --no-emit-project -o requirements.txt

# 提交更改
git add pyproject.toml uv.lock requirements.txt
git commit -m "chore: 移除 package-name"
git push
```

## 本地开发

### 安装依赖

```bash
# 安装所有依赖（包括开发依赖）
uv sync

# 只安装生产依赖
uv sync --no-dev
```

### 运行应用

```bash
# 使用 uv 运行
uv run uvicorn app.main:app --reload

# 或者激活虚拟环境后运行
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

uvicorn app.main:app --reload
```

## Docker 部署

Docker 构建时会：
1. 复制 `requirements.txt`
2. 使用 pip 从清华镜像源安装依赖
3. 复制应用代码
4. 启动应用

### 本地测试 Docker 构建

```bash
# 构建镜像
docker-compose build

# 运行容器
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止容器
docker-compose down
```

## 重要文件说明

| 文件 | 作用 | 是否提交到 Git |
|------|------|----------------|
| `pyproject.toml` | 项目配置和依赖声明 | ✅ 是 |
| `uv.lock` | 锁定的依赖版本（精确版本） | ✅ 是 |
| `requirements.txt` | Docker 部署用的依赖列表 | ✅ 是 |
| `.venv/` | 本地虚拟环境 | ❌ 否（.gitignore） |
| `.uv/` | uv 缓存目录 | ❌ 否（.gitignore） |

## 常见问题

### Q: 为什么不直接在 Docker 中使用 uv？

A: 
- uv 在 Docker 中会创建虚拟环境（不必要）
- pip 安装更简单、更快
- requirements.txt 兼容性更好

### Q: 为什么要提交 uv.lock？

A: 
- 确保团队成员使用相同的依赖版本
- 便于追踪依赖变更历史
- 提供精确的版本锁定

### Q: 如何查看依赖树？

```bash
# 查看依赖关系
uv tree

# 查看特定包的依赖
uv tree --package fastapi
```

### Q: 如何检查过时的依赖？

```bash
# 检查可更新的包
uv lock --dry-run --upgrade
```

## 最佳实践

1. **定期更新依赖**：每月检查并更新依赖
2. **测试后再部署**：更新依赖后在本地测试
3. **记录重大变更**：在 CHANGELOG.md 中记录依赖更新
4. **锁定关键版本**：对于关键依赖，使用精确版本号

## 自动化脚本

创建一个便捷脚本 `update_requirements.sh`：

```bash
#!/bin/bash
# 更新 requirements.txt

echo "导出 requirements.txt..."
uv export --no-dev --no-hashes --no-emit-project -o requirements.txt

echo "✅ requirements.txt 已更新"
echo "请检查更改并提交："
echo "  git add requirements.txt"
echo "  git commit -m 'chore: 更新 requirements.txt'"
```

使用方法：
```bash
chmod +x update_requirements.sh
./update_requirements.sh
```

