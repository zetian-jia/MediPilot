# 🔧 MediPilot 开发者文档

## 目录

1. [项目架构深度解析](#项目架构深度解析)
2. [代码审查报告](#代码审查报告)
3. [核心模块详解](#核心模块详解)
4. [扩展开发指南](#扩展开发指南)
5. [测试与调试](#测试与调试)
6. [性能优化建议](#性能优化建议)
7. [安全最佳实践](#安全最佳实践)

---

## 项目架构深度解析

### 整体设计哲学

MediPilot 采用**分层解耦**的设计模式，灵感来源于**感知-认知-执行**的人类行为模型：

```
输入（屏幕） → 感知层 → 认知层 → 执行层 → 输出（操作）
              ↓         ↓         ↓
            隐私保护   AI推理   安全机制
```

### 模块依赖关系图

```
┌─────────────────────────────────────────────────────┐
│                    main.py                          │
│              (任务编排与流程控制)                    │
└────────┬──────────────┬──────────────┬──────────────┘
         │              │              │
         ▼              ▼              ▼
┌────────────┐  ┌──────────────┐  ┌──────────────┐
│ Perception │  │  Cognition   │  │  Execution   │
│   感知层   │  │    认知层     │  │   执行层     │
└────────────┘  └──────────────┘  └──────────────┘
         │              │              │
         ▼              ▼              ▼
┌────────────────────────────────────────────────────┐
│                 configs/settings.py                │
│                  (全局配置中心)                     │
└────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────┐
│              medipilot/utils/logger.py             │
│                (审计日志系统)                       │
└────────────────────────────────────────────────────┘
```

---

## 代码审查报告

### 项目优势 ✅

#### 1. **架构清晰，职责分明**

- ✅ 三层架构（感知-认知-执行）完全解耦
- ✅ 单一职责原则：每个模块只负责一件事
- ✅ 依赖注入：通过配置文件管理全局参数

#### 2. **安全机制完善**

- ✅ **本地隐私过滤**：PII数据不离开本地网络
- ✅ **紧急熔断机制**：PyAutoGUI FAILSAFE
- ✅ **审计日志**：所有操作可追溯
- ✅ **动作限速**：模拟人类操作节奏

#### 3. **医疗场景适配**

- ✅ 医疗术语映射表（[`medipilot.py`](medipilot.py:23-40)）
- ✅ 临床专用Prompt策略
- ✅ 法律免责声明机制
- ✅ 置信度评估系统

#### 4. **代码质量**

- ✅ 完整的中文注释和文档字符串
- ✅ 错误处理机制（try-except）
- ✅ 类型提示（虽未全面使用）
- ✅ 模块化设计便于测试

### 潜在改进点 ⚠️

#### 1. **类型注解不完整**

**现状**：
```python
def capture(self):
    """高频低延迟截屏"""
    # ...
```

**建议改进**：
```python
from PIL import Image

def capture(self) -> Image.Image:
    """高频低延迟截屏
    
    Returns:
        PIL.Image.Image: 原始截图对象
    """
    # ...
```

#### 2. **缺少单元测试**

**建议**：
- 为每个核心功能编写单元测试
- 使用 `pytest` 框架
- Mock外部API调用

#### 3. **配置验证不足**

**建议**：
在 [`configs/settings.py`](configs/settings.py:7-49) 中添加配置验证：

```python
class Config:
    def __init__(self):
        self._validate_config()
    
    def _validate_config(self):
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY未配置")
        if not self.OPENAI_API_KEY.startswith('sk-'):
            raise ValueError("API密钥格式错误")
```

#### 4. **日志级别使用不够精细**

**建议**：
- `DEBUG`: 详细的内部状态
- `INFO`: 常规操作流程
- `WARNING`: 潜在问题（如置信度低）
- `ERROR`: 操作失败
- `CRITICAL`: 系统级错误

#### 5. **重复代码**

**发现**：[`medipilot.py`](medipilot.py) 和模块化版本存在大量重复。

**建议**：
- 移除 `medipilot.py` 或将其作为"快速入门示例"
- 统一使用模块化版本

---

## 核心模块详解

### 1. 感知层 (Perception Layer)

**文件位置**：[`medipilot/perception/screen.py`](medipilot/perception/screen.py)

#### 类：`Perception`

##### 方法详解

###### `__init__(self)`

初始化MSS截屏对象。

**复杂度**：O(1)  
**依赖**：`mss` 库

###### `capture(self) -> Image.Image`

捕获当前屏幕。

**技术细节**：
- 使用 `mss.mss()` 的零拷贝截屏
- 支持多显示器（默认主显示器）
- 性能：约 10-30ms/帧

**返回格式**：PIL Image (RGB)

###### `privacy_filter(self, image: Image.Image) -> Image.Image`

本地PII脱敏。

**算法**：
1. PIL Image → NumPy数组
2. 提取ROI区域
3. 应用高斯模糊（核：99x99，sigma=30）
4. 替换原图对应区域
5. NumPy数组 → PIL Image

**性能考虑**：
- 高斯模糊是O(n)操作
- 对于1080p图像，耗时约10-20ms

**可配置参数**：
- `PRIVACY_REGION`: 在 [`configs/settings.py`](configs/settings.py:36)

###### `apply_som_overlay(self, image: Image.Image, grid_size: int = 80) -> Image.Image`

叠加视觉网格。

**网格编码逻辑**：
```python
# 列：A, B, C, ... Z, AA, AB, ...
# 行：0, 1, 2, 3, ...
# 示例：第0列第5行 → A5
```

**视觉效果**：
- 红色网格线（RGB: 255,0,0）
- 每个交叉点标注坐标
- 便于AI定位UI元素

---

### 2. 认知层 (Cognition Layer)

**文件位置**：[`medipilot/cognition/engine.py`](medipilot/cognition/engine.py)

#### 类：`Brain`

##### 方法详解

###### `__init__(self, model: str = config.VISION_MODEL)`

初始化OpenAI客户端。

**支持的模型**：
- `gpt-4o` (推荐)
- `gpt-4-turbo`
- `gpt-4-vision-preview`

###### `_encode_image(self, image: Image.Image) -> str`

图像Base64编码。

**编码流程**：
1. PIL Image → BytesIO
2. 保存为JPEG (quality=85)
3. Base64编码
4. 返回UTF-8字符串

**性能**：
- 对于1080p图像，编码后约200-400KB
- 耗时：约50-100ms

###### `call_vision(self, image: Image.Image, prompt: str) -> dict`

调用视觉大模型API。

**请求结构**：
```json
{
  "model": "gpt-4o",
  "messages": [
    {
      "role": "system",
      "content": "你是一个极其严谨的医疗自动化助手..."
    },
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "<prompt>"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
      ]
    }
  ],
  "response_format": {"type": "json_object"}
}
```

**错误处理**：
- 捕获所有异常
- 返回错误信息给执行层
- 记录到审计日志

#### 类：`Prompts`

医疗专用提示词库。

##### `extraction()` - 数据提取Prompt

**设计要点**：
1. **明确角色定位**："临床检验数据分析专家"
2. **结构化输出**：强制JSON格式
3. **领域知识融入**：指标单位、参考范围
4. **质量控制**：置信度评估

**输出Schema**：
```json
{
  "thought": "对图像的分析过程",
  "findings": [
    {
      "metric": "指标名称",
      "value": "数值",
      "confidence": 0.0-1.0,
      "target_field_hint": "目标字段提示"
    }
  ],
  "scan_quality": "High/Normal/Low"
}
```

##### `operation(task_state)` - UI操作Prompt

**设计要点**：
1. **上下文传递**：当前任务状态
2. **视觉导航**：基于SoM网格定位
3. **安全约束**：禁止危险操作
4. **决策透明**：要求说明reasoning

**输出Schema**：
```json
{
  "thought": "当前UI状态分析",
  "action": "click | type | finish",
  "coordinate": [x, y],
  "text": "输入内容（如有）",
  "reasoning": "操作依据"
}
```

---

### 3. 执行层 (Execution Layer)

**文件位置**：[`medipilot/execution/action.py`](medipilot/execution/action.py)

#### 类：`Executor`

##### 安全机制详解

###### PAUSE (动作限速)

**原理**：PyAutoGUI在每个动作后自动等待。

**配置**：[`configs/settings.py`](configs/settings.py:30)
```python
PAUSE_INTERVAL = 0.8  # 秒
```

**目的**：
- 模拟人类操作节奏
- 防止系统卡顿
- 留出反应时间

###### FAILSAFE (紧急熔断)

**原理**：鼠标移至屏幕四角触发 `FailSafeException`。

**启用**：[`configs/settings.py`](configs/settings.py:32)
```python
FAILSAFE = True
```

**触发条件**：
- 鼠标坐标 (0, 0)
- 或任意屏幕角落

##### 方法详解

###### `execute(self, plan: dict) -> bool`

执行AI生成的操作指令。

**支持的动作**：

| 动作类型 | 实现方式 | 关键参数 |
|----------|----------|----------|
| `click` | `pyautogui.moveTo()` + `click()` | coordinate: [x, y] |
| `type` | `pyautogui.click()` + `write()` | coordinate, text |
| `finish` | 返回True | 无 |

**平滑移动**：
```python
pyautogui.moveTo(coord[0], coord[1], duration=0.5)
```
- `duration=0.5`: 0.5秒过渡动画
- 轨迹：贝塞尔曲线插值

**文本输入**：
```python
pyautogui.write(str(text), interval=0.1)
```
- `interval=0.1`: 每个字符间隔0.1秒
- 模拟人类打字速度

---

### 4. 配置系统

**文件位置**：[`configs/settings.py`](configs/settings.py)

#### 类：`Config`

**设计模式**：单例模式

**配置分类**：

##### API配置
```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
```

##### 模型选择
```python
VISION_MODEL = os.getenv("VISION_MODEL", "gpt-4o")
EXTRACTION_MODEL = os.getenv("EXTRACTION_MODEL", "gpt-4o")
```

##### 系统参数
```python
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
SCREENSHOT_DELAY = float(os.getenv("SCREENSHOT_DELAY", 1.0))
```

##### 安全配置
```python
PAUSE_INTERVAL = 0.8
FAILSAFE = True
PRIVACY_REGION = (0, 150, 0, 400)  # [y1, y2, x1, x2]
```

##### 法律声明
```python
DISCLAIMER_TEXT = """..."""
```

---

### 5. 日志系统

**文件位置**：[`medipilot/utils/logger.py`](medipilot/utils/logger.py)

#### 功能：`setup_logger(name: str = "MediPilot")`

**日志架构**：

```
┌─────────────────────────────────────┐
│         Logger Instance             │
│      (logging.getLogger)            │
└────────┬────────────────┬───────────┘
         │                │
         ▼                ▼
┌─────────────────┐  ┌──────────────┐
│  File Handler   │  │Console Handler│
│  (审计存档)     │  │ (实时监控)    │
└─────────────────┘  └──────────────┘
```

**日志格式**：

- **文件**：`%(asctime)s - [%(levelname)s] - [临床操作审计] - %(message)s`
- **控制台**：`%(asctime)s - [%(levelname)s] - %(message)s`

**日志轮转**：
- 按日期归档：`medipilot_YYYY-MM-DD.log`
- 建议实现大小轮转（未实现）

**使用示例**：
```python
from medipilot.utils.logger import audit_logger

audit_logger.info("常规操作")
audit_logger.warning("潜在风险")
audit_logger.error("操作失败")
audit_logger.critical("系统崩溃")
```

---

## 扩展开发指南

### 1. 添加新的医疗指标

#### 步骤1：更新术语映射

编辑 [`medipilot.py`](medipilot.py:23-40)：

```python
class MedicalTranslator:
    MAPPING = {
        # 现有指标
        "WBC": "白细胞计数",
        "RBC": "红细胞计数",
        # 新增指标
        "CRP": "C反应蛋白",
        "ESR": "血沉",
        "ALT": "丙氨酸氨基转移酶",
        "AST": "天门冬氨酸氨基转移酶",
    }
```

#### 步骤2：更新Prompt

编辑 [`medipilot/cognition/engine.py`](medipilot/cognition/engine.py:69-103)：

```python
@staticmethod
def extraction():
    return """
    # 提取规范
    1. WBC (白细胞计数): 单位通常为 10^9/L
    2. RBC (红细胞计数): 单位通常为 10^12/L
    3. CRP (C反应蛋白): 单位通常为 mg/L  # 新增
    4. ESR (血沉): 单位通常为 mm/h       # 新增
    ...
    """
```

### 2. 支持新的模型提供商

#### 示例：集成Anthropic Claude

**步骤1**：安装依赖
```bash
pip install anthropic
```

**步骤2**：修改 [`medipilot/cognition/engine.py`](medipilot/cognition/engine.py:8-19)：

```python
from openai import OpenAI
from anthropic import Anthropic

class Brain:
    def __init__(self, model=config.VISION_MODEL, provider="openai"):
        self.model = model
        self.provider = provider
        
        if provider == "openai":
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        elif provider == "anthropic":
            self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        else:
            raise ValueError(f"不支持的提供商: {provider}")
```

**步骤3**：适配API调用格式

### 3. 添加新的操作类型

#### 示例：支持 `scroll` 动作

编辑 [`medipilot/execution/action.py`](medipilot/execution/action.py:17-62)：

```python
def execute(self, plan):
    action = plan.get("action")
    
    # 现有动作 ...
    
    elif action == "scroll":
        direction = plan.get("direction", "down")
        amount = plan.get("amount", -500)
        
        if direction == "down":
            pyautogui.scroll(amount)
        else:
            pyautogui.scroll(-amount)
        
        audit_logger.info(f"滚动屏幕: {direction}, 量: {amount}")
    
    # ...
```

更新Prompt以支持新动作：

```python
@staticmethod
def operation(task_state):
    return f"""
    # 动作序列：
    - 'click': 点击输入框
    - 'type': 输入文本
    - 'scroll': 滚动页面  # 新增
    - 'finish': 完成任务
    """
```

---

## 测试与调试

### 单元测试框架

#### 安装pytest
```bash
pip install pytest pytest-cov pytest-mock
```

#### 测试示例：感知层

创建 `tests/test_perception.py`：

```python
import pytest
from PIL import Image
from medipilot.perception.screen import Perception

@pytest.fixture
def perception():
    return Perception()

@pytest.fixture
def sample_image():
    # 创建测试图像
    return Image.new('RGB', (800, 600), color='white')

def test_capture(perception):
    """测试截屏功能"""
    img = perception.capture()
    assert isinstance(img, Image.Image)
    assert img.size[0] > 0
    assert img.size[1] > 0

def test_privacy_filter(perception, sample_image):
    """测试隐私过滤"""
    filtered = perception.privacy_filter(sample_image)
    assert isinstance(filtered, Image.Image)
    assert filtered.size == sample_image.size

def test_som_overlay(perception, sample_image):
    """测试SoM网格叠加"""
    marked = perception.apply_som_overlay(sample_image, grid_size=80)
    assert isinstance(marked, Image.Image)
    # 验证图像已修改（像素值不同）
    assert marked != sample_image
```

#### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定文件
pytest tests/test_perception.py

# 查看覆盖率
pytest --cov=medipilot tests/
```

### 调试技巧

#### 1. 保存中间图像

在开发时保存处理过程中的图像：

```python
# 在 medipilot/perception/screen.py 中
def privacy_filter(self, image):
    cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # 调试：保存原图
    cv2.imwrite("debug_original.jpg", cv_img)
    
    # 应用模糊
    roi = cv_img[y1:y2, x1:x2]
    blurred_roi = cv2.GaussianBlur(roi, (99, 99), 30)
    cv_img[y1:y2, x1:x2] = blurred_roi
    
    # 调试：保存处理后的图像
    cv2.imwrite("debug_filtered.jpg", cv_img)
    
    return Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
```

#### 2. 详细日志

临时提升日志级别：

```python
# 在 .env 中
LOG_LEVEL=DEBUG
```

#### 3. 交互式调试

使用IPython：

```python
# 在代码中插入断点
import IPython; IPython.embed()
```

---

## 性能优化建议

### 1. 图像处理优化

#### 问题：高斯模糊耗时较长

**当前实现**：
```python
blurred_roi = cv2.GaussianBlur(roi, (99, 99), 30)
```

**优化方案**：
- 使用更小的核（如 51x51）
- 降低sigma值
- 考虑使用快速模糊算法（如Box Blur）

**性能对比**：
| 方法 | 核大小 | 耗时 (1080p) |
|------|--------|--------------|
| 高斯模糊 | 99x99 | ~20ms |
| 高斯模糊 | 51x51 | ~8ms |
| Box Blur | 51x51 | ~3ms |

### 2. API调用优化

#### 问题：频繁API调用成本高

**优化策略**：

1. **缓存机制**：
```python
class Brain:
    def __init__(self):
        self.cache = {}
    
    def call_vision(self, image, prompt):
        # 生成图像哈希作为缓存键
        img_hash = hashlib.md5(image.tobytes()).hexdigest()
        cache_key = f"{img_hash}_{prompt}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # 正常API调用
        result = # ...
        self.cache[cache_key] = result
        return result
```

2. **批量处理**：将多个小任务合并为一次API调用

### 3. 截屏频率优化

#### 问题：1秒采样一次可能过于频繁

**动态调整**：
```python
class Perception:
    def __init__(self):
        self.idle_count = 0
        self.delay = 1.0
    
    def adaptive_delay(self):
        # UI未变化时延长间隔
        if self.idle_count > 5:
            return self.delay * 2
        return self.delay
```

---

## 安全最佳实践

### 1. API密钥管理

#### ❌ 错误做法

```python
# 硬编码在代码中
OPENAI_API_KEY = "sk-proj-xxxx"
```

#### ✅ 正确做法

```bash
# 使用 .env 文件
echo "OPENAI_API_KEY=sk-proj-xxxx" > .env

# 或使用系统环境变量
export OPENAI_API_KEY="sk-proj-xxxx"
```

### 2. 输入验证

#### 示例：坐标验证

```python
def execute(self, plan):
    coord = plan.get("coordinate")
    
    # 验证坐标有效性
    if coord:
        if not isinstance(coord, list) or len(coord) != 2:
            audit_logger.error("坐标格式错误")
            return False
        
        x, y = coord
        screen_w, screen_h = pyautogui.size()
        
        if not (0 <= x <= screen_w and 0 <= y <= screen_h):
            audit_logger.error(f"坐标越界: ({x}, {y})")
            return False
```

### 3. 异常处理

#### 分层错误处理

```python
# 感知层
try:
    img = self.capture()
except Exception as e:
    audit_logger.critical(f"截屏失败: {e}")
    return None

# 认知层
try:
    result = self.call_vision(img, prompt)
except APIError as e:
    audit_logger.error(f"API调用失败: {e}")
    return {"action": "error", "reason": str(e)}

# 执行层
try:
    self.execute(plan)
except FailSafeException:
    audit_logger.warning("用户触发紧急停止")
    raise
```

### 4. 数据脱敏验证

#### 测试脱敏效果

```python
import cv2
import numpy as np

def verify_privacy_filter():
    """验证隐私过滤是否有效"""
    perception = Perception()
    original = perception.capture()
    filtered = perception.privacy_filter(original)
    
    # 提取ROI区域
    y1, y2, x1, x2 = config.PRIVACY_REGION
    original_roi = np.array(original)[y1:y2, x1:x2]
    filtered_roi = np.array(filtered)[y1:y2, x1:x2]
    
    # 计算差异
    diff = np.abs(original_roi.astype(float) - filtered_roi.astype(float))
    mean_diff = np.mean(diff)
    
    # 确保有足够的模糊效果
    assert mean_diff > 10, "隐私过滤效果不足"
    print(f"✅ 隐私过滤有效，平均差异: {mean_diff}")
```

---

## 贡献指南

### 代码风格

- **PEP 8**：遵循Python官方风格指南
- **注释**：中文注释，解释"为什么"而非"是什么"
- **文档字符串**：Google风格

### 提交规范

```bash
# 格式：<type>(<scope>): <subject>

# 类型:
# feat: 新功能
# fix: 修复bug
# docs: 文档更新
# style: 代码格式
# refactor: 重构
# test: 测试
# chore: 构建/工具

# 示例:
git commit -m "feat(cognition): 添加Claude模型支持"
git commit -m "fix(perception): 修复隐私过滤区域计算错误"
```

---

## 常见开发陷阱

### 1. 忘记激活虚拟环境

```bash
# ❌ 全局安装可能导致版本冲突
pip install -r requirements.txt

# ✅ 使用虚拟环境
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 硬编码配置

```python
# ❌ 不要硬编码
PRIVACY_REGION = (0, 150, 0, 400)

# ✅ 从配置读取
from configs.settings import config
PRIVACY_REGION = config.PRIVACY_REGION
```

### 3. 忽略异常处理

```python
# ❌ 裸露的API调用
response = client.chat.completions.create(...)

# ✅ 完整错误处理
try:
    response = client.chat.completions.create(...)
except Exception as e:
    audit_logger.error(f"API调用失败: {e}")
    return None
```

---

## 版本发布流程

### 1. 版本号规范

遵循 **语义化版本** (Semantic Versioning)：

```
MAJOR.MINOR.PATCH

例如: 1.2.3
- MAJOR: 重大变更（不兼容旧版本）
- MINOR: 新功能（向后兼容）
- PATCH: Bug修复
```

### 2. 发布检查清单

- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] CHANGELOG.md 已更新
- [ ] 版本号已更新
- [ ] Git标签已创建

---

**文档最后更新**：2026-01-08  
**维护者**：MediPilot Development Team