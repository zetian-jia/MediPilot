# 📚 MediPilot API 参考文档

## 目录

1. [感知层 API](#感知层-api)
2. [认知层 API](#认知层-api)
3. [执行层 API](#执行层-api)
4. [配置系统 API](#配置系统-api)
5. [日志系统 API](#日志系统-api)
6. [数据结构定义](#数据结构定义)

---

## 感知层 API

### `medipilot.perception.screen.Perception`

屏幕捕获与图像处理类。

#### 构造函数

```python
Perception()
```

**描述**：初始化感知层对象，创建MSS截屏实例。

**示例**：
```python
from medipilot.perception.screen import Perception

perception = Perception()
```

---

#### `capture()`

```python
def capture(self) -> PIL.Image.Image
```

**描述**：捕获当前屏幕截图。

**返回值**：
- `PIL.Image.Image`: RGB格式的PIL图像对象

**异常**：
- `RuntimeError`: 截屏失败时抛出

**示例**：
```python
image = perception.capture()
print(f"截图尺寸: {image.size}")  # (1920, 1080)
```

**性能**：约10-30ms/帧

---

#### `privacy_filter(image)`

```python
def privacy_filter(self, image: PIL.Image.Image) -> PIL.Image.Image
```

**描述**：对图像中的敏感信息区域进行本地模糊处理。

**参数**：
- `image` (PIL.Image.Image): 待处理的原始图像

**返回值**：
- `PIL.Image.Image`: 脱敏后的图像

**配置**：
- 模糊区域由 `config.PRIVACY_REGION` 定义
- 格式：`(y1, y2, x1, x2)`

**算法**：
- 高斯模糊核：99x99
- Sigma值：30

**示例**：
```python
original = perception.capture()
safe_image = perception.privacy_filter(original)
safe_image.save("safe_screenshot.png")
```

**注意事项**：
⚠️ 确保 `PRIVACY_REGION` 完全覆盖所有敏感信息区域

---

#### `apply_som_overlay(image, grid_size=80)`

```python
def apply_som_overlay(
    self, 
    image: PIL.Image.Image, 
    grid_size: int = 80
) -> PIL.Image.Image
```

**描述**：在图像上叠加SoM（Set-of-Mark）视觉网格。

**参数**：
- `image` (PIL.Image.Image): 待处理图像
- `grid_size` (int, optional): 网格大小（像素），默认80

**返回值**：
- `PIL.Image.Image`: 叠加网格后的图像

**网格编码规则**：
- 列：A, B, C, ..., Z, AA, AB, ...
- 行：0, 1, 2, 3, ...
- 示例：第2列第5行 = B5

**视觉效果**：
- 网格颜色：红色 (255, 0, 0)
- 线宽：1像素
- 标签字体：系统默认

**示例**：
```python
# 默认80x80网格
marked_img = perception.apply_som_overlay(image)

# 自定义120x120网格（适用于4K屏幕）
marked_img = perception.apply_som_overlay(image, grid_size=120)
```

**推荐配置**：
| 分辨率 | 推荐grid_size |
|--------|---------------|
| 1920x1080 | 80 |
| 2560x1440 | 100 |
| 3840x2160 | 140 |

---

## 认知层 API

### `medipilot.cognition.engine.Brain`

AI推理引擎类。

#### 构造函数

```python
Brain(model: str = config.VISION_MODEL)
```

**描述**：初始化AI大脑，创建OpenAI客户端。

**参数**：
- `model` (str, optional): 使用的模型名称，默认从配置读取

**支持的模型**：
- `gpt-4o` (推荐)
- `gpt-4-turbo`
- `gpt-4-vision-preview`
- `claude-3-5-sonnet` (需额外配置)

**示例**：
```python
from medipilot.cognition.engine import Brain

# 使用默认模型
brain = Brain()

# 指定模型
brain = Brain(model="gpt-4-turbo")
```

---

#### `call_vision(image, prompt)`

```python
def call_vision(
    self, 
    image: PIL.Image.Image, 
    prompt: str
) -> dict
```

**描述**：调用视觉大模型进行多模态推理。

**参数**：
- `image` (PIL.Image.Image): 输入图像
- `prompt` (str): 任务提示词

**返回值**：
- `dict`: JSON格式的模型响应

**返回格式**：
```python
{
    "thought": "AI的思考过程",
    "action": "操作类型",
    "coordinate": [x, y],  # 可选
    "text": "文本内容",     # 可选
    "reasoning": "操作理由"
}
```

**异常处理**：
- 自动捕获所有API错误
- 返回错误信息而非抛出异常

**错误返回格式**：
```python
{
    "action": "error",
    "reason": "错误详细信息"
}
```

**示例**：
```python
from medipilot.cognition.engine import Brain, Prompts

brain = Brain()
image = perception.capture()

# 数据提取
result = brain.call_vision(image, Prompts.extraction())

# UI操作
plan = brain.call_vision(image, Prompts.operation("录入WBC数据"))
```

**性能指标**：
- 平均响应时间：2-5秒
- Base64编码耗时：50-100ms
- 图像大小：200-400KB（1080p）

---

### `medipilot.cognition.engine.Prompts`

医疗专用提示词库。

#### `extraction()`

```python
@staticmethod
def extraction() -> str
```

**描述**：生成化验单数据提取Prompt。

**返回值**：
- `str`: 完整的提示词文本

**提取指标**：
- WBC (白细胞)
- RBC (红细胞)
- Hgb (血红蛋白)
- PLT (血小板)

**输出Schema**：
```json
{
  "thought": "分析过程",
  "findings": [
    {
      "metric": "WBC",
      "value": "7.2",
      "confidence": 0.98,
      "target_field_hint": "白细胞"
    }
  ],
  "scan_quality": "High"
}
```

**示例**：
```python
prompt = Prompts.extraction()
result = brain.call_vision(lab_report_image, prompt)

for finding in result["findings"]:
    print(f"{finding['metric']}: {finding['value']}")
```

---

#### `operation(task_state)`

```python
@staticmethod
def operation(task_state: str) -> str
```

**描述**：生成UI自动化操作Prompt。

**参数**：
- `task_state` (str): 当前任务状态描述

**返回值**：
- `str`: 完整的提示词文本

**支持的动作**：
- `click`: 点击指定坐标
- `type`: 输入文本
- `finish`: 完成任务

**输出Schema**：
```json
{
  "thought": "UI状态分析",
  "action": "click",
  "coordinate": [450, 600],
  "text": null,
  "reasoning": "点击输入框以获得焦点"
}
```

**示例**：
```python
task_state = "已提取WBC=7.2，现在需要在EMR系统中找到对应输入框"
prompt = Prompts.operation(task_state)
plan = brain.call_vision(screen_image, prompt)

print(f"下一步动作: {plan['action']}")
print(f"理由: {plan['reasoning']}")
```

---

## 执行层 API

### `medipilot.execution.action.Executor`

GUI自动化执行器。

#### 构造函数

```python
Executor()
```

**描述**：初始化执行器，配置PyAutoGUI安全参数。

**安全配置**：
- `PAUSE`: 动作间隔0.8秒
- `FAILSAFE`: 启用紧急停止

**示例**：
```python
from medipilot.execution.action import Executor

executor = Executor()
```

---

#### `execute(plan)`

```python
def execute(self, plan: dict) -> bool
```

**描述**：根据AI生成的计划执行GUI操作。

**参数**：
- `plan` (dict): AI生成的操作指令

**计划格式**：
```python
{
    "action": "click | type | finish",
    "coordinate": [x, y],     # 对于click和type
    "text": "输入内容",        # 仅对于type
    "reasoning": "操作理由"
}
```

**返回值**：
- `bool`: 
  - `True`: 任务完成
  - `False`: 继续执行

**支持的动作详解**：

##### 1. `click` - 点击

```python
plan = {
    "action": "click",
    "coordinate": [450, 600],
    "reasoning": "点击输入框"
}
```

**行为**：
1. 平滑移动至目标坐标（0.5秒）
2. 执行点击
3. 记录日志

##### 2. `type` - 输入文本

```python
plan = {
    "action": "type",
    "coordinate": [450, 600],
    "text": "7.2",
    "reasoning": "输入WBC数值"
}
```

**行为**：
1. 点击坐标以聚焦
2. 逐字符输入（0.1秒/字符）
3. 记录日志

##### 3. `finish` - 完成

```python
plan = {
    "action": "finish",
    "reasoning": "所有数据已录入"
}
```

**行为**：
1. 记录完成日志
2. 返回 `True`

**异常**：
- `pyautogui.FailSafeException`: 用户触发紧急停止

**示例**：
```python
# 执行点击
plan = {"action": "click", "coordinate": [500, 300]}
is_done = executor.execute(plan)

# 执行输入
plan = {
    "action": "type", 
    "coordinate": [500, 300],
    "text": "7.2"
}
is_done = executor.execute(plan)

# 完成任务
if is_done:
    print("任务执行完毕")
```

---

## 配置系统 API

### `configs.settings.Config`

全局配置类。

#### 属性列表

##### API配置

```python
OPENAI_API_KEY: str
```
OpenAI API密钥，从环境变量 `OPENAI_API_KEY` 读取。

```python
OPENAI_BASE_URL: str
```
API基础URL，默认 `https://api.openai.com/v1`。

##### 模型配置

```python
VISION_MODEL: str
```
视觉理解模型，默认 `gpt-4o`。

```python
EXTRACTION_MODEL: str
```
数据提取模型，默认 `gpt-4o`。

##### 系统参数

```python
LOG_LEVEL: str
```
日志级别：`DEBUG | INFO | WARNING | ERROR`，默认 `INFO`。

```python
SCREENSHOT_DELAY: float
```
截屏间隔（秒），默认 `1.0`。

##### 安全配置

```python
PAUSE_INTERVAL: float
```
动作执行间隔（秒），默认 `0.8`。

```python
FAILSAFE: bool
```
紧急熔断开关，默认 `True`。

```python
PRIVACY_REGION: tuple
```
隐私保护区域 `(y1, y2, x1, x2)`，默认 `(0, 150, 0, 400)`。

##### 法律声明

```python
DISCLAIMER_TEXT: str
```
医疗免责声明文本。

#### 使用示例

```python
from configs.settings import config

# 读取配置
print(f"当前模型: {config.VISION_MODEL}")
print(f"截屏间隔: {config.SCREENSHOT_DELAY}秒")

# 访问隐私区域
y1, y2, x1, x2 = config.PRIVACY_REGION
```

---

## 日志系统 API

### `medipilot.utils.logger.audit_logger`

全局审计日志实例。

#### 日志方法

##### `debug(message)`

```python
audit_logger.debug("详细调试信息")
```

**用途**：记录详细的内部状态信息。

##### `info(message)`

```python
audit_logger.info("常规操作流程")
```

**用途**：记录正常的操作流程。

##### `warning(message)`

```python
audit_logger.warning("潜在风险警告")
```

**用途**：记录可能的问题或异常情况。

##### `error(message)`

```python
audit_logger.error("操作失败信息")
```

**用途**：记录操作失败或错误。

##### `critical(message)`

```python
audit_logger.critical("系统级严重错误")
```

**用途**：记录系统崩溃或不可恢复的错误。

#### 日志格式

**文件日志**：
```
2026-01-08 15:30:00 - [INFO] - [临床操作审计] - MediPilot启动
```

**控制台日志**：
```
2026-01-08 15:30:00 - [INFO] - MediPilot启动
```

#### 日志文件

**路径**：`logs/medipilot_YYYY-MM-DD.log`

**编码**：UTF-8

**轮转**：按日期自动归档

---

## 数据结构定义

### 提取结果 (Extraction Result)

```python
{
    "thought": str,              # AI的分析过程
    "findings": [                # 提取的指标列表
        {
            "metric": str,       # 指标名称 (如 "WBC")
            "value": str,        # 数值 (如 "7.2")
            "unit": str,         # 单位 (如 "10^9/L")
            "confidence": float, # 置信度 (0.0-1.0)
            "target_field_hint": str  # 目标字段提示
        }
    ],
    "scan_quality": str          # 扫描质量: High/Normal/Low
}
```

### 操作计划 (Operation Plan)

```python
{
    "thought": str,              # AI的思考过程
    "action": str,               # 动作类型: click/type/finish
    "coordinate": [int, int],    # 坐标 [x, y]（可选）
    "text": str,                 # 输入文本（可选）
    "reasoning": str             # 操作理由
}
```

### 医疗数据 (Medical Data)

```python
{
    "report_id": str,            # 报告ID
    "patient_info": {
        "name": str,             # 患者姓名（脱敏）
        "age": int,              # 年龄
        "department": str        # 科室
    },
    "findings": [                # 检验结果
        {
            "metric": str,       # 指标名称
            "value": str,        # 数值
            "unit": str,         # 单位
            "ref_range": str     # 参考范围
        }
    ],
    "extraction_confidence": float,  # 提取置信度
    "timestamp": str             # ISO 8601时间戳
}
```

---

## 完整使用示例

### 端到端工作流

```python
from medipilot.perception.screen import Perception
from medipilot.cognition.engine import Brain, Prompts
from medipilot.execution.action import Executor
from medipilot.utils.logger import audit_logger
import time

# 1. 初始化组件
perception = Perception()
brain = Brain()
executor = Executor()

audit_logger.info("系统初始化完成")

# 2. 捕获并处理图像
raw_image = perception.capture()
safe_image = perception.privacy_filter(raw_image)
marked_image = perception.apply_som_overlay(safe_image)

audit_logger.info("图像处理完成")

# 3. 提取数据
extraction_prompt = Prompts.extraction()
data = brain.call_vision(marked_image, extraction_prompt)

audit_logger.info(f"提取到 {len(data['findings'])} 个指标")

# 4. 执行UI操作
task_state = f"已提取数据: {data}"
operation_prompt = Prompts.operation(task_state)

while True:
    # 获取当前屏幕
    current_screen = perception.capture()
    safe_screen = perception.privacy_filter(current_screen)
    marked_screen = perception.apply_som_overlay(safe_screen)
    
    # 决策下一步
    plan = brain.call_vision(marked_screen, operation_prompt)
    
    # 执行动作
    is_done = executor.execute(plan)
    
    if is_done:
        audit_logger.info("任务完成")
        break
    
    time.sleep(1)
```

---

## 版本历史

### v1.0.0 (2026-01-08)

**初始发布**

- ✅ 感知层：截屏、隐私过滤、SoM网格
- ✅ 认知层：GPT-4o集成、医疗Prompt
- ✅ 执行层：GUI自动化、安全机制
- ✅ 配置系统：环境变量管理
- ✅ 日志系统：审计追踪

---

## 许可证

本API文档遵循 MIT 许可证。

---

**最后更新**：2026-01-08  
**维护者**：MediPilot Development Team