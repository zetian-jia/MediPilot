# 🩺 MediPilot 用户使用手册

## 📋 目录

1. [项目概述](#项目概述)
2. [系统架构](#系统架构)
3. [安装指南](#安装指南)
4. [配置说明](#配置说明)
5. [使用流程](#使用流程)
6. [核心功能详解](#核心功能详解)
7. [安全与合规](#安全与合规)
8. [常见问题](#常见问题)
9. [故障排除](#故障排除)
10. [开发者指南](#开发者指南)

---

## 项目概述

### 什么是 MediPilot？

**MediPilot** 是一款专为临床医生设计的智能自动化助手（AI Agent），旨在解决医疗工作中繁琐的数据录入问题。它通过先进的多模态大语言模型和计算机视觉技术，实现电子病历（EMR）系统中检验数据的自动化提取与录入。

### 核心价值

- **🔄 消除重复劳动**：自动从PDF检验报告或扫描件中提取关键指标（如WBC、Hgb等），并自动填写至EMR系统
- **🔒 本地隐私保护**：内置隐私过滤器，在数据上传前对病人姓名、病案号等敏感信息进行本地模糊处理
- **👁️ 视觉导航技术**：采用SoM（Set-of-Mark）视觉锚点技术，使AI能像人眼一样理解复杂的临床UI界面
- **📝 审计日志追溯**：自动记录每一步操作及AI的"思考过程"，生成完整的审计日志

### ⚠️ 重要声明

**本软件仅供医疗研究与工作效率辅助使用**

1. **必须复核**：AI生成的所有操作和提取的数据**必须**由具有执业资格的医师进行人工复核
2. **风险自担**：由于未复核或不可抗力导致的医疗差错，开发者及本项目不承担任何法律责任
3. **合规性**：请确保在符合所在医疗机构数据安全政策的前提下使用

---

## 系统架构

MediPilot 采用三层架构设计：

```
┌─────────────────────────────────────────┐
│           感知层 (Perception)            │
│  - 屏幕截图采集                          │
│  - PII本地脱敏处理                       │
│  - SoM视觉锚点叠加                       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│           认知层 (Cognition)             │
│  - 多模态大模型推理                      │
│  - 医疗专用Prompt策略                    │
│  - 结构化数据提取                        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│           执行层 (Execution)             │
│  - GUI自动化操作                         │
│  - 动作限速与安全停机                    │
│  - 审计日志记录                          │
└─────────────────────────────────────────┘
```

### 目录结构

```
MediPilot/
├── main.py                    # 主程序入口
├── medipilot.py              # 独立完整版本（可选）
├── requirements.txt          # Python依赖包
├── .env.example             # 环境变量模板
├── README.md                # 项目说明
├── configs/
│   └── settings.py          # 全局配置文件
├── medipilot/
│   ├── perception/          # 感知层模块
│   │   └── screen.py       # 截屏与图像处理
│   ├── cognition/           # 认知层模块
│   │   └── engine.py       # AI推理引擎
│   ├── execution/           # 执行层模块
│   │   └── action.py       # GUI操作执行器
│   └── utils/               # 工具模块
│       └── logger.py        # 审计日志系统
├── tests/
│   └── mock_data.py         # 测试数据
├── logs/                    # 日志目录（自动生成）
└── docs/                    # 文档目录
    └── USER_GUIDE.md        # 本文档
```

---

## 安装指南

### 系统要求

- **操作系统**：Windows 10/11, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python版本**：Python 3.8 或更高版本
- **内存**：建议 8GB RAM 以上
- **网络**：需要稳定的互联网连接（调用云端大模型API）
- **屏幕分辨率**：建议 1920x1080 或更高

### 步骤 1：克隆项目

```bash
# 通过 Git 克隆仓库
git clone https://github.com/zetian-jia/MediPilot.git

# 进入项目目录
cd MediPilot
```

### 步骤 2：创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

### 步骤 3：安装依赖

```bash
pip install -r requirements.txt
```

**依赖包说明：**

| 包名 | 版本 | 用途 |
|------|------|------|
| openai | ≥1.0.0 | OpenAI API客户端 |
| python-dotenv | ≥1.0.0 | 环境变量管理 |
| pyautogui | ≥0.9.54 | GUI自动化 |
| mss | ≥9.0.1 | 高性能截屏 |
| opencv-python | ≥4.8.0 | 图像处理 |
| numpy | ≥1.24.0 | 数值计算 |
| Pillow | ≥10.0.0 | 图像操作 |

---

## 配置说明

### 步骤 1：创建配置文件

```bash
# 复制示例配置文件
cp .env.example .env
```

### 步骤 2：配置 API 密钥

编辑 `.env` 文件，填入您的API密钥：

```ini
# OpenAI API 配置
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# 可选：使用 Anthropic Claude
# ANTHROPIC_API_KEY=sk-ant-your-key-here

# 模型选择
VISION_MODEL=gpt-4o           # 视觉理解模型
EXTRACTION_MODEL=gpt-4o       # 数据提取模型

# 系统参数
LOG_LEVEL=INFO                # 日志级别: DEBUG, INFO, WARNING, ERROR
SCREENSHOT_DELAY=1.0          # 截屏间隔（秒）
```

### 步骤 3：配置隐私保护区域

根据您使用的EMR系统界面，需要在 [`configs/settings.py`](configs/settings.py:36) 中调整隐私保护区域：

```python
# 隐私保护区域 (ROI): [y1, y2, x1, x2]
# 默认覆盖左上角病人信息区域
PRIVACY_REGION = (0, 150, 0, 400)
```

**如何确定隐私区域坐标：**

1. 打开您的EMR系统
2. 截取一张屏幕截图
3. 使用图像编辑工具（如画图、Photoshop）测量病人信息区域的坐标
4. 更新 `PRIVACY_REGION` 参数

---

## 使用流程

### 快速开始

#### 1. 启动程序

```bash
python main.py
```

#### 2. 确认免责声明

程序启动后会显示法律免责声明：

```
============================================================
【严正声明 / DISCLAIMER】
1. 本软件 (MediPilot) 仅作为临床辅助工具，用于自动化繁琐的录入工作。
2. 软件提供的所有数据提取和操作建议，**必须** 经过执业医师的人工复核。
3. 严禁将本软件用于无人监管的自动诊疗决策。
4. 开发者不对因未复核导致的医疗差错承担法律责任。

继续使用即代表您已知悉并同意上述条款。
============================================================
我已阅读并知悉上述临床风险 (y/n): 
```

输入 `y` 继续。

#### 3. 工作流程

程序将自动执行以下步骤：

1. **感知阶段**：
   - 捕获当前屏幕截图
   - 对敏感信息区域进行本地模糊处理
   - 叠加SoM视觉网格

2. **认知决策阶段**：
   - 将处理后的图像发送至大模型
   - AI分析当前任务状态并制定操作计划

3. **执行阶段**：
   - 根据AI生成的指令执行GUI操作
   - 记录操作日志

#### 4. 紧急停止

如需立即停止程序：

- **键盘中断**：按 `Ctrl+C`
- **鼠标安全停机**：将鼠标快速移至屏幕四角任一角落

### 典型使用场景

#### 场景 1：化验单数据录入

**任务描述**：从PDF化验单中提取WBC、RBC、Hgb、PLT指标，并录入EMR系统。

**操作步骤**：

1. 打开PDF化验单和EMR系统录入界面
2. 启动 MediPilot
3. 程序自动：
   - 识别化验单中的指标值
   - 定位EMR系统中的输入框
   - 自动填写数据
4. **医师复核**确认数据准确性

#### 场景 2：多患者批量录入

**注意事项**：

- 每位患者的数据录入完成后，**必须**手动切换至下一位患者
- 确保隐私过滤区域正确覆盖患者信息
- 建议每录入5-10位患者后休息，检查日志

---

## 核心功能详解

### 1. 感知层 (Perception)

#### 高频截屏 (`capture()`)

使用 MSS 库实现毫秒级截屏，确保实时响应。

**代码位置**：[`medipilot/perception/screen.py`](medipilot/perception/screen.py:16-26)

```python
def capture(self):
    """高频低延迟截屏"""
    monitor = self.sct.monitors[1]
    sct_img = self.sct.grab(monitor)
    return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
```

#### 隐私过滤器 (`privacy_filter()`)

在本地对敏感信息进行高斯模糊处理，**确保PII数据不离开本地网络**。

**代码位置**：[`medipilot/perception/screen.py`](medipilot/perception/screen.py:28-56)

**技术细节**：
- 使用99x99高斯核
- 模糊强度参数：30
- 处理区域可配置

#### SoM视觉锚点 (`apply_som_overlay()`)

在图像上叠加红色网格和坐标标签（如A1, B2），帮助AI理解UI布局。

**代码位置**：[`medipilot/perception/screen.py`](medipilot/perception/screen.py:58-97)

**网格规格**：
- 默认网格大小：80x80像素
- 标签格式：列字母+行数字（A0, B1...）
- 颜色：红色 (255, 0, 0)

### 2. 认知层 (Cognition)

#### AI推理引擎 (`Brain`)

调用OpenAI GPT-4o或其他多模态模型进行视觉推理。

**代码位置**：[`medipilot/cognition/engine.py`](medipilot/cognition/engine.py:8-63)

**关键特性**：
- 支持Base64图像编码
- JSON结构化输出
- 完整的错误处理机制

#### 医疗专用Prompt策略

**数据提取Prompt** ([`Prompts.extraction()`](medipilot/cognition/engine.py:70-103))：

专门用于从化验单中提取结构化数据，包含：
- 指标识别规范
- 单位换算逻辑
- 交叉核对机制
- 置信度评估

**UI操作Prompt** ([`Prompts.operation()`](medipilot/cognition/engine.py:106-138))：

用于指导AI进行界面操作，包含：
- 视觉网格定位
- 动作序列规划
- 安全禁令（防止误操作）

### 3. 执行层 (Execution)

#### GUI自动化 (`Executor`)

基于PyAutoGUI实现鼠标键盘操作。

**代码位置**：[`medipilot/execution/action.py`](medipilot/execution/action.py:6-62)

**支持的操作类型**：

| 操作类型 | 说明 | 参数 |
|----------|------|------|
| `click` | 点击指定坐标 | coordinate: [x, y] |
| `type` | 输入文本 | coordinate: [x, y], text: "内容" |
| `finish` | 完成任务 | 无 |

**安全机制**：

1. **动作限速**：每个操作间隔0.8秒（可配置）
2. **FAILSAFE**：鼠标移至屏幕角落自动停止
3. **平滑移动**：鼠标移动使用0.5秒过渡动画

---

## 安全与合规

### 数据隐私保护

#### 1. 本地脱敏处理

所有包含患者信息的区域在发送至云端API前，已在本地完成模糊化处理。

**技术实现**：
- 高斯模糊算法（OpenCV）
- 核大小：99x99
- 处理区域可自定义

#### 2. 最小化数据传输

仅传输必要的视觉信息，**不传输**：
- 患者姓名
- 病案号
- 身份证号
- 其他PII数据

#### 3. 审计日志

所有操作均记录在本地日志文件中。

**日志路径**：`logs/medipilot_YYYY-MM-DD.log`

**日志内容示例**：

```
2026-01-08 15:30:00 - [INFO] - [临床操作审计] - MediPilot 临床助手开始运行...
2026-01-08 15:30:01 - [INFO] - [临床操作审计] - 感知模块初始化完成
2026-01-08 15:30:02 - [DEBUG] - [临床操作审计] - 已应用隐私过滤: 区域 (0, 150, 0, 400)
2026-01-08 15:30:05 - [INFO] - [临床操作审计] - 正在发送视觉请求至大模型...
2026-01-08 15:30:08 - [INFO] - [临床操作审计] - 模型思考结果: 化验单数据显示 WBC 为 7.2...
2026-01-08 15:30:09 - [INFO] - [临床操作审计] - 执行动作: [click] | 理由: 点击输入框以获得焦点
```

### 医疗合规性

#### 必须遵守的原则

1. **人工复核**：所有AI录入的数据必须由医师复核
2. **有监督使用**：禁止无人值守运行
3. **定期审计**：建议每周检查日志文件
4. **数据备份**：重要日志应定期备份

#### 推荐的使用场景

✅ **适用**：
- 常规检验数据录入
- 重复性高的标准化表单填写
- 医师监督下的批量数据处理

❌ **不适用**：
- 紧急医疗决策
- 无人值守的自动化诊疗
- 涉及处方药物的操作（除非有明确的二次确认）

---

## 常见问题

### Q1: 程序启动后无反应？

**可能原因**：
1. 未配置API密钥
2. 网络连接问题
3. 依赖包未正确安装

**解决方案**：
```bash
# 检查 .env 文件是否存在且已配置
cat .env

# 测试网络连接
ping api.openai.com

# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

### Q2: 隐私过滤不生效？

**解决方案**：

1. 检查 [`configs/settings.py`](configs/settings.py:36) 中的 `PRIVACY_REGION` 配置
2. 使用截图工具确认坐标准确性
3. 查看日志中是否有警告信息

### Q3: AI点击位置不准确？

**可能原因**：
- 屏幕分辨率与训练数据差异较大
- SoM网格大小不适配

**解决方案**：

调整网格大小（[`medipilot/perception/screen.py`](medipilot/perception/screen.py:58)）：

```python
# 对于高分辨率屏幕 (4K)，增大网格
img_with_som = perception.apply_som_overlay(img, grid_size=120)

# 对于低分辨率屏幕，减小网格
img_with_som = perception.apply_som_overlay(img, grid_size=60)
```

### Q4: API调用超时？

**解决方案**：

1. 检查网络稳定性
2. 考虑使用国内API中转服务
3. 调整 `OPENAI_BASE_URL` 指向中转地址

### Q5: 日志文件过大？

**解决方案**：

定期清理旧日志或实现日志轮转：

```bash
# 删除30天前的日志
find logs/ -name "*.log" -mtime +30 -delete
```

---

## 故障排除

### 诊断步骤

#### 1. 检查日志

```bash
# 查看最新日志
tail -f logs/medipilot_$(date +%Y-%m-%d).log
```

#### 2. 测试API连接

创建测试脚本 `test_api.py`：

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "测试连接"}]
)
print("✅ API连接正常")
print(response.choices[0].message.content)
```

#### 3. 验证屏幕捕获

```python
from medipilot.perception.screen import Perception

p = Perception()
img = p.capture()
img.save("test_screenshot.png")
print("✅ 截图已保存至 test_screenshot.png")
```

### 常见错误代码

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `InvalidAPIKey` | API密钥无效 | 检查 .env 文件中的密钥 |
| `RateLimitError` | 超出API调用限额 | 等待或升级API套餐 |
| `ConnectionError` | 网络连接失败 | 检查网络或代理设置 |
| `FailSafeException` | 鼠标触发安全停机 | 正常现象，重新启动即可 |

---

## 开发者指南

### 自定义任务

修改 [`main.py`](main.py:30) 中的任务描述：

```python
task_desc = "从屏幕显示的化验单中提取 WBC, RBC, Hgb, PLT 指标，并录入到电子病历系统对应的输入框中。"
```

### 添加新的医疗指标

在 [`medipilot.py`](medipilot.py:23-40) 的 `MedicalTranslator` 中添加映射：

```python
MAPPING = {
    "WBC": "白细胞计数",
    "RBC": "红细胞计数",
    # 添加新指标
    "CRP": "C反应蛋白",
    "ESR": "血沉",
}
```

### 自定义Prompt

修改 [`medipilot/cognition/engine.py`](medipilot/cognition/engine.py:69-138) 中的Prompt模板以适配特定场景。

### 测试模式

使用模拟数据进行测试：

```bash
python tests/mock_data.py
```

### 性能优化建议

1. **减少API调用**：缓存重复的视觉分析结果
2. **批量处理**：将多个操作合并为一次API调用
3. **本地模型**：考虑使用本地部署的小型模型进行简单决策

---

## 项目贡献

欢迎提交Issue和Pull Request！

**贡献指南**：
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](../LICENSE) 文件。

---

## 联系方式

- **项目主页**：https://github.com/zetian-jia/MediPilot
- **问题反馈**：https://github.com/zetian-jia/MediPilot/issues
- **开发者**：Zetian Jia

---

**最后更新时间**：2026-01-08  
**文档版本**：v1.0

---

## 附录

### A. 完整配置文件示例

```ini
# .env 完整配置示例

# ===== OpenAI API 配置 =====
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.openai.com/v1

# ===== Anthropic Claude 配置（可选）=====
# ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx

# ===== 模型选择 =====
VISION_MODEL=gpt-4o
EXTRACTION_MODEL=gpt-4o

# ===== 系统参数 =====
LOG_LEVEL=INFO
SCREENSHOT_DELAY=1.0

# ===== 性能调优 =====
# PAUSE_INTERVAL=0.8
# FAILSAFE=True
```

### B. 支持的模型列表

| 模型 | 提供商 | 视觉能力 | 推荐用途 |
|------|--------|----------|----------|
| gpt-4o | OpenAI | ✅ | 全场景推荐 |
| gpt-4-turbo | OpenAI | ✅ | 成本优化 |
| claude-3-5-sonnet | Anthropic | ✅ | 复杂推理 |
| claude-3-opus | Anthropic | ✅ | 高精度要求 |

### C. 快捷键参考

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+C` | 终止程序 |
| 鼠标移至屏幕角落 | 触发安全停机 |

---

**感谢您使用 MediPilot！** 如有任何问题或建议，欢迎通过GitHub Issues联系我们。