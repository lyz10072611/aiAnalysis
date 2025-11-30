## 污染物监测分析平台（FastAPI + Vue 3）

一个用于对城市空气污染物进行时空分析的全栈示例项目，后端基于 **FastAPI + PostgreSQL + SQLAlchemy**，前端基于 **Vue 3 + Vite + TypeScript + Chart.js**。

界面以中文为主，主要能力包括：

- **站点与污染物管理**：从数据库读取监测站点、污染物元数据；
- **监测数据融合分析**：按站点 / 污染物 / 日期范围，对地面监测 `measurements` 与 TIF 反演数据 `measurements_tif` 进行对齐与合并；
- **可视化与统计**：
  - 站点值 vs TIF 值时间序列折线图；
  - 平均值 / 最大值等统计指标；
  - 原始逐小时数据表格与差值展示；
- **接口化访问**：前端通过 REST API 访问后端分析结果，便于集成到其他系统。

---

### 项目结构

```text
polllutants-aiAnalysis/
├─ backend/            # FastAPI 后端
│  ├─ app/
│  │  ├─ main.py       # FastAPI 入口，挂载路由与 CORS
│  │  ├─ config.py     # 配置中心（数据库、CORS 等）
│  │  ├─ database.py   # SQLAlchemy Engine / Session 工具
│  │  ├─ models.py     # ORM 模型：站点、污染物、监测数据、TIF 数据
│  │  ├─ crud.py       # 数据访问与分析逻辑
│  │  ├─ schemas.py    # Pydantic 模型（输入/输出）
│  │  └─ routers/
│  │     └─ analysis.py  # 对外 API 路由定义
│  └─ requirements.txt   # 后端依赖
│
└─ frontend/           # Vue 3 + Vite 前端
   ├─ src/
   │  ├─ App.vue       # 主界面布局与数据流
   │  ├─ main.ts       # Vue 挂载入口
   │  ├─ components/   # 业务组件（筛选、图表、表格、指标看板）
   │  ├─ services/
   │  │  └─ api.ts     # 与 FastAPI 通信的 Axios 封装
   │  └─ types.ts      # 前端 TypeScript 类型定义
   ├─ package.json     # 前端依赖与脚本
   └─ vite.config.ts   # Vite 配置
```

---

### 后端配置说明

- 配置文件：`backend/app/config.py`，使用 `pydantic-settings` 管理。
- 默认数据库连接（可通过环境变量覆盖）：

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=aiAnalysis
DB_USER=postgres
DB_PASSWORD=postgres
```

- CORS 配置：
  - 默认允许的前端来源：
    - `http://localhost:5173`
    - `http://localhost:5174`
  - 可通过环境变量 `CORS_ORIGINS` 配置（逗号分隔），如：

```bash
CORS_ORIGINS=http://localhost:5174,http://localhost:3000
```

- API 前缀：`/api`（`Settings.api_prefix`），当前路由统一挂载在该前缀下。

---

### 前后端依赖概览

#### 后端（`backend/requirements.txt`）

- **fastapi==0.110.2**：Web 框架
- **uvicorn[standard]==0.30.1**：ASGI 服务器
- **SQLAlchemy==2.0.25**：ORM/数据库访问
- **psycopg2-binary==2.9.9**：PostgreSQL 驱动
- **pydantic-settings==2.2.1**：配置管理

#### 前端（`frontend/package.json`）

- **vue**：3.4.x，前端框架
- **axios**：HTTP 客户端，请求 FastAPI
- **chart.js** + **vue-chartjs**：图表绘制
- 开发依赖：`vite`, `typescript`, `vue-tsc`, `@vitejs/plugin-vue`, `@types/node` 等。

---

### 快速部署（本地开发环境）

> 前置要求：本地已安装 **Python 3.10+**、**Node.js 18+**、**PostgreSQL**。

#### 1. 准备数据库

1. 在 PostgreSQL 中创建数据库 `aiAnalysis`：

   ```sql
   CREATE DATABASE "aiAnalysis" WITH ENCODING 'UTF8';
   ```

2. 根据实际情况执行建表脚本（如有）或通过 Alembic/手动建表；
3. 将监测站点 / 污染物 / 监测数据 / TIF 数据导入对应数据表。

#### 2. 后端部署

```bash
cd backend

# （可选）创建虚拟环境
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动 FastAPI 服务（默认端口 8000）
uvicorn app.main:app --reload --port 8000
```

服务启动后，可以用浏览器或 curl 访问：

```bash
http://localhost:8000/
http://localhost:8000/docs
```

#### 3. 前端部署

```bash
cd frontend
npm install

# 开发模式（默认端口 5173，如被占用可能为 5174）
npm run dev -- --host
```

终端会输出如 `http://localhost:5173` 或 `http://localhost:5174` 的访问地址。

---

### 快速启动流程（推荐步骤）

1. **启动 PostgreSQL**，确保数据库 `aiAnalysis` 可访问；
2. **启动后端**：
   - 在 `backend/` 目录执行：
     ```bash
     uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
     ```
   - 打开浏览器访问 `http://localhost:8000/docs`，确认 API 正常；
3. **启动前端**：
   - 在 `frontend/` 目录执行：
     ```bash
     npm run dev -- --host
     ```
   - 根据输出访问前端地址（如 `http://localhost:5174`）；
4. 在前端界面中：
   - 左侧查看数据库连接状态；
   - 通过筛选面板选择站点、污染物与时间范围；
   - 查看折线图、统计指标与表格中展示的站点值/TIF 值对比。

---

### API 概览

- **`GET /api/sites`**
  - 功能：返回所有监测站点信息。
  - 响应字段：`site_id`, `site_name`, `longitude`, `latitude`。

- **`GET /api/pollutants`**
  - 功能：返回支持的污染物列表。
  - 响应字段：`pollutant_id`, `pollutant_name`。

- **`GET /api/analysis`**
  - 功能：在给定站点、污染物和日期范围内，返回对齐后的地面监测值与 TIF 值时序数据。
  - 查询参数：
    - `site_id`: 站点 ID
    - `pollutant_id`: 污染物 ID
    - `start_date`: 开始日期（`YYYY-MM-DD`）
    - `end_date`: 结束日期（`YYYY-MM-DD`）
  - 响应字段：`date`, `hour`, `timestamp`, `stationValue`, `tifValue`。
