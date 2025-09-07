# 弹幕任务监控器

这是一个用于监控弹幕服务后台任务完成情况并通过Telegram发送通知的工具。


## 快速部署

### 使用 Docker Compose（推荐）

1. 创建 `docker-compose.yml` 文件：

```yaml
version: "3.8"

services:
  # 弹幕任务监控器服务
  danmaku-task-monitor:
    image: qixiuyuano/danmaku-task-monitor:latest
    container_name: danmaku-task-monitor
    restart: unless-stopped
    
    # 数据和日志持久化
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs

    # 环境变量配置
    environment:
      # 弹幕服务API必填配置
      - API_BASE_URL=弹幕服务API基础地址
      - API_KEY=弹幕服务API密钥
      
      # Telegram通知必填配置
      - TELEGRAM_BOT_TOKEN=Telegram机器人Token
      - TELEGRAM_CHAT_ID=接收通知的聊天ID
      
      # 时区配置（可选，默认Asia/Shanghai）
      - TZ=Asia/Shanghai
      
      # 其他可选配置
      - CHECK_INTERVAL=60
      - TIME_WINDOW_BUFFER=60
      - MAX_TASKS_TO_PROCESS=50
      - LOG_LEVEL=INFO
      - LOG_BACKUP_COUNT=7
```

2. 启动服务：

```bash
docker-compose up -d
```

### 环境变量说明

#### 必填配置

- `API_BASE_URL`: 弹幕服务API基础地址
- `API_KEY`: 弹幕服务API密钥
- `TELEGRAM_BOT_TOKEN`: Telegram机器人Token
- `TELEGRAM_CHAT_ID`: 接收通知的聊天ID

#### 可选配置

- `CHECK_INTERVAL`: 检查间隔(秒，默认60秒)
- `TIME_WINDOW_BUFFER`: 时间窗口缓冲(秒，默认60秒)
- `MAX_TASKS_TO_PROCESS`: 每次最多处理的任务数(默认50个)
- `LOG_BACKUP_COUNT`: 日志文件保留天数(默认7天)
- `TZ`: 时区设置(默认Asia/Shanghai)

### 本地开发

1. 克隆项目：

```bash
git clone https://github.com/QiXiuYuano/danmaku-task-monitor.git
cd danmaku-task-monitor
```

2. 复制配置文件：

```bash
cp .env.example .env
```

3. 编辑 `.env` 文件，填入必要的配置

4. 安装依赖并运行：

```bash
pip install -r requirements.txt
python -m src.main
```

## 功能特性

- 🎯 实时监控弹幕服务后台任务状态
- 📢 通过Telegram发送任务完成通知
- 🔁 自动去重处理，避免重复通知
- ⏱️ 可配置的检查间隔和时间窗口


## 许可证

MIT License