# 🩺 MediPilot: 医疗场景自动化 AI Agent

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

MediPilot 是一款专为医疗行业设计的自主 AI Agent，基于多模态大模型（GPT-4o/Claude 3.5）和计算机视觉技术。它能够像医生一样“观察”屏幕、理解化验单内容并自动操作电子病历（EMR）系统。

---

## 🚀 核心价值：解决医疗痛点

1.  **打破“信息孤岛”**：自动跨系统读取 PDF/扫描件化验单，无需人工手动录入，大幅降低医疗差错。
2.  **语义术语对齐**：内置医疗翻译模块，自动处理缩写（如 WBC -> 白细胞计数）与系统表单的映射。
3.  **合规隐私保护**：独有的 **Privacy Filter** 机制，在数据离屏前本地自动模糊病人 PII 敏感信息。
4.  **安全可控操作**：通过 **SoM (Set-of-Mark)** 视觉锚点技术确保点击精准，并配备紧急熔断保护。

---

## 🛠️ 项目架构

项目采用模块化设计，清晰划分感知、认知与执行边界：

*   **`medipilot/perception/`**：感知层。负责截屏、本地 PII 脱敏、SoM 网格叠加。
*   **`medipilot/cognition/`**：认知层。多模态逻辑推理、双阶段 Prompt 策略（数据提取 & 动作决策）。
*   **`medipilot/execution/`**：执行层。跨平台 GUI 驱动（PyAutoGUI），包含动作限速与安全熔断。
*   **`configs/`**：全局配置管理，支持通过 `.env` 快速切换模型与 API 环境。

---

## 📦 安装指南

### 1. 克隆与环境准备
确保已安装 Python 3.8 或以上版本。

```bash
# 克隆仓库 (示例)
git clone https://github.com/your-repo/MediPilot.git
cd MediPilot

# 安装核心依赖
pip install -r requirements.txt
```

### 2. 配置环境变量
项目使用 `.env` 文件管理敏感信息。

```bash
# 从模板创建配置文件
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API 信息：
```ini
OPENAI_API_KEY=sk-your-key-here
VISION_MODEL=gpt-4o
```

---

## 📝 使用方法

### 运行主程序
启动后，MediPilot 将进入自动观察模式。默认任务是从化验单提取 WBC 指标并填入系统。

```bash
python main.py
```

### 关键组件说明
*   **隐私保护**：程序运行过程中，会自动在左上角病人信息区施加高斯模糊，保护数据合规。
*   **视觉定位**：屏幕上会看到红色网格标签（如 A1, B2），这是 Agent 理解位置的“地图”。
*   **安全停止**：若需紧急停止，只需将鼠标快速移动到屏幕的 **任意角落**。

---

## 📂 目录结构预览
```text
MediPilot/
├── medipilot/           # 核心代码包
│   ├── perception/      # 视觉与截屏处理
│   ├── cognition/       # 大模型逻辑与 Prompts
│   └── execution/       # GUI 动作执行
├── configs/             # 配置文件管理
├── .env                 # 环境变量 (用户创建)
├── requirements.txt     # 依赖包列表
├── main.py              # 程序入口
└── README.md            # 项目说明文档
```

---

## ⚠️ 免责声明
本软件仅用于研究与效率辅助目的。所有由 AI 生成的操作和文书内容必须经过执业医师审核。开发者对任何由于自动化操作导致的医疗事故不承担法律责任。
