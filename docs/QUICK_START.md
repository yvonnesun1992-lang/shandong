# shandong Quick Start

shandong 是一个本地股票量化研究与模拟交易平台原型。

当前版本仅用于学习、研究、历史回测和模拟交易演示：

- 不连接真实券商
- 不自动下单
- 不做实盘交易
- 不构成投资建议
- 历史回测不代表未来收益

## Windows 新手运行步骤

### 1. 打开项目目录

在 PowerShell 或命令提示符中进入项目目录：

```powershell
cd D:\HuaweiMoveData\Users\Yvonne\Documents\codex\shandong
```

### 2. 创建虚拟环境

```powershell
python -m venv .venv
```

### 3. 激活虚拟环境

```powershell
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 阻止脚本运行，可以执行：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

然后重新激活虚拟环境。

### 4. 安装依赖

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. 运行测试

```powershell
python -m pytest
```

### 6. 启动 dashboard

```powershell
streamlit run app/main.py
```

打开浏览器访问 Streamlit 提示的本地地址，通常是：

```text
http://localhost:8501
```

## 一键启动方式

推荐使用：

```powershell
python scripts/start_dashboard.py
```

Windows 也可以双击或运行：

```powershell
start_shandong.bat
```

PowerShell 用户也可以运行：

```powershell
.\start_shandong.ps1
```

## 启动前诊断

如果 dashboard 无法启动，先运行：

```powershell
python scripts/system_doctor.py
```

诊断脚本会检查：

- Python 版本
- pandas / numpy / matplotlib / streamlit / yfinance / akshare / pytest 是否可 import
- config、sample data、cache、reports 等关键目录
- settings、watchlists、paper portfolio 和示例数据文件
- 系统健康检查中心结果

## 常见问题

### pip 安装失败

先升级 pip：

```powershell
python -m pip install --upgrade pip
```

再重新安装：

```powershell
pip install -r requirements.txt
```

### PowerShell 无法激活虚拟环境

运行：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

然后重新执行：

```powershell
.\.venv\Scripts\Activate.ps1
```

### streamlit 命令找不到

确认已安装依赖：

```powershell
pip install -r requirements.txt
```

也可以用 Python 模块方式启动：

```powershell
python -m streamlit run app/main.py
```

### yfinance 或 akshare 数据失败

系统会优先尝试真实行情数据。如果数据源失败，会使用本地示例数据 fallback，让趋势评分、图表和回测仍然可以演示。

示例数据只用于功能演示，不代表真实行情，不构成投资建议。

### dashboard 端口被占用

可以指定其他端口：

```powershell
streamlit run app/main.py --server.port 8502
```

## sample fallback、cache、health check 的作用

- sample fallback：真实数据源失败时使用本地示例数据，保证页面可以演示。
- cache：把行情数据保存到本地，减少重复请求。
- health check：检查本地配置、缓存、报告、示例数据和安全边界，帮助定位启动问题。

## 安全边界

shandong 当前阶段不会：

- 连接真实券商
- 自动下单
- 保存真实账户、密码、API key、secret、token 或券商凭证
- 调用 OpenAI API 或任何外部 AI API
- 使用 AI 预测股价

