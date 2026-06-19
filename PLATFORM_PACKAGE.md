# V1.31 Platform Layer

## 架构说明

V1.31 将系统从单一产品入口升级为平台架构雏形，新增四个轻量平台层：

- `src/plugins/`：插件系统，提供统一注册和运行接口。
- `src/api/`：FastAPI 服务层，提供标准 JSON API。
- `src/core/user_context.py`：逻辑用户上下文，用于报告、缓存和看板隔离。
- `app/platform.py`：Platform Launcher，按 INIT -> CONFIG -> CACHE -> PLUGINS -> API -> UI 初始化。

本版本只新增平台边界和服务入口，不改变现有策略计算、风险计算、报告评分或回测逻辑。

## Plugin System

插件系统包含：

- `PluginBase`
- `PluginRegistry`
- `ReportPlugin`
- `StrategyPlugin`
- `RiskPlugin`
- `DashboardPlugin`

插件可以独立注册、查询和运行。默认 registry 会注册 report、strategy、risk、dashboard 四个插件，主系统可通过 registry 动态调用插件能力。

## API 说明

API 服务入口为 `src/api/server.py`，所有接口返回统一结构：

```json
{
  "status": "success",
  "data": {},
  "warning": []
}
```

已提供接口：

- `POST /api/report/generate`
- `GET /api/report/list`
- `GET /api/report/detail`
- `GET /api/trend`
- `GET /api/compare`
- `GET /api/risk`
- `GET /api/dashboard/summary`

API 层只包装本地研究结果和插件返回值，不连接外部交易系统。

## User Isolation

`UserContext` 默认 `user_id = "default"`，并提供：

- `report_namespace`
- `report_key()`
- `cache_key()`
- `dashboard_key()`

隔离方式为逻辑 namespace 隔离，不包含登录系统、支付系统或真实账号体系。

## Launcher 说明

`app/platform.py` 提供 `initialize_platform()`，初始化顺序为：

```text
INIT -> CONFIG -> CACHE -> PLUGINS -> API -> UI
```

返回对象包含 user context、cache manager、plugin registry、FastAPI app 和 UI 入口信息。

## 安全边界

V1.31 继续遵守以下边界：

- 不连接券商。
- 不自动下单。
- 不生成真实交易指令。
- 不预测股价。
- 不调用 AI API。
- 不调用 OpenAI API。
- 不保存 API key、secret、password、token。
- 不新增支付系统。
- 不新增真实登录系统。
- 不改变核心策略逻辑。

## V1.31 版本说明

V1.31 是平台架构层，不是功能堆叠版本。目标是让现有策略研究系统具备 SaaS-ready foundation 的基本形态：

- 有插件边界。
- 有 API 服务入口。
- 有逻辑用户隔离。
- 有统一 Platform Launcher。
- 有可测试的平台稳定性基础。
