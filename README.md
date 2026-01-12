# Agent_1：基于 Gemini 2.0 的多模态智能体基础框架

## 项目概述

本项目旨在构建一个基于 Google Gemini 2.0 的智能体“基础大脑”，首先实现命令行（CLI）对话助手，并为后续的桌面自动化和虚拟环境具身智能打下基础。

第一阶段目标：
- 与 Gemini 2.0 API 完整对接（使用 google-genai 官方 SDK）
- 实现连续对话的 CLI 聊天机器人
- 提供可选的语音输入识别与语音播报能力

## 环境要求

- Python 3.10+
- Node.js 18+（后续阶段使用，当前阶段仅需安装）
- 操作系统：Windows 10/11

## 安装指南

1. 克隆或下载仓库代码
2. 创建并激活 Python 虚拟环境（示例以 venv 为例）：

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

4. 配置环境变量（推荐使用 PowerShell 或系统环境变量）：

   - 设置 Gemini API Key：

     ```powershell
     $env:GEMINI_API_KEY="你的_API_Key"
     ```

   - 可选：指定默认模型与系统提示词文件路径：

     ```powershell
     $env:GEMINI_MODEL="gemini-2.0-flash"
     $env:SYSTEM_PROMPT_PATH="config/system_prompt.txt"
     ```

## 使用说明

### 1. 运行文本模式 CLI 助手

```bash
python -m src.main --mode text
```

- 直接在终端输入中文或英文问题
- 输入 `exit` 或 `quit` 结束会话

### 2. 运行语音模式 CLI 助手（可选）

语音模式依赖额外库和本机音频设备支持：

```bash
pip install -r requirements.txt
python -m src.main --mode voice
```

需要正常工作的麦克风和扬声器，程序会：
- 监听你的语音输入
- 使用本地语音识别将其转为文本
- 调用 Gemini 2.0 得到回复
- 通过 TTS 将回复朗读出来

### 3. 系统提示词与人格配置

- 默认系统提示词保存在 `config/system_prompt.txt`
- 可以通过修改该文件或设置 `SYSTEM_PROMPT_PATH` 环境变量，动态切换人格设定与安全策略

## 项目结构

- `src/`：主代码目录
  - `main.py`：CLI 入口，支持文本/语音两种模式
  - `config.py`：API Key、模型名称和系统提示词加载
  - `conversation.py`：对话历史管理与 Gemini 调用封装
  - `voice_io.py`：语音输入/输出能力封装
  - `logging_utils.py`：日志配置
- `config/`：
  - `system_prompt.txt`：默认人格设定与系统提示词
- `tests/`：单元测试
  - `test_config.py`：配置加载逻辑测试
  - `test_conversation.py`：对话历史和请求构造测试
- `requirements.txt`：Python 依赖列表

## 测试

项目使用 `pytest` 编写和运行单元测试：

```bash
pip install pytest
pytest
```

当前测试覆盖：
- 配置加载与环境变量读取
- 对话历史管理与基础请求构造

## 后续扩展方向

- 丰富异常处理与日志采集，满足生产级可观测性
- 将 CLI 对话能力嵌入桌面助手和游戏智能体
- 引入更完善的提示词模板与安全策略配置

