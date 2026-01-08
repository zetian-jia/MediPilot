# 🩺 MediPilot: 临床医生 AI 自动化副驾驶

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**MediPilot** 是一款专为临床医生设计的自主 AI Agent。它通过多模态大模型与计算机视觉技术，实现电子病历 (EMR) 系统中繁琐数据的自动化录入与跨系统对齐。

---

## ⚠️ 严正声明 (Disclaimer)

**本软件仅供医疗研究与工作效率辅助使用。**

1.  **必须复核**：AI 生成的所有操作和提取的数据**必须**由具有执业资格的医师进行人工复核。
2.  **风险自担**：由于未复核或不可抗力导致的医疗差错，开发者及本项目不承担任何法律责任。
3.  **合规性**：请确保在符合所在医疗机构数据安全政策的前提下使用。

---

## 🚀 核心临床价值

*   **消除重复劳动**：自动从检验报告 (PDF/扫描件) 提取 WBC、Hgb 等指标，并自动填写至 EMR 系统。
*   **本地隐私保护**：内置 **Privacy Filter**，在数据传输前自动在本地对病人姓名、病案号等 PII 信息进行高斯模糊。
*   **视觉导航技术**：采用 **SoM (Set-of-Mark)** 视觉锚点，使 AI 能像人眼一样理解复杂的临床 UI 界面。
*   **临床审计日志**：自动记录每一步操作及其“思考过程”，生成审计日志 (Audit Trail)，便于追溯。

---

## 🛠️ 项目架构

*   **`medipilot/perception/`**：感知层。负责截屏、本地 PII 脱敏、SoM 网格叠加。
*   **`medipilot/cognition/`**：认知层。多模态逻辑推理、医疗专用 Prompt 策略。
*   **`medipilot/execution/`**：执行层。驱动 GUI 操作（PyAutoGUI），包含动作限速与**鼠标悬停安全停机**机制。
*   **`medipilot/utils/logger.py`**：审计日志模块。
*   **`configs/settings.py`**：集中管理临床参数与法律声明。

---

## 📦 快速开始

### 1. 环境准备
```bash
# 克隆仓库
git clone https://github.com/zetian-jia/MediPilot.git
cd MediPilot

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置文件
创建 `.env` 文件并填入您的 API 密钥：
```ini
OPENAI_API_KEY=sk-your-key-here
VISION_MODEL=gpt-4o
```

### 3. 启动程序
```bash
python main.py
```
*启动后请务必阅读并确认命令行弹出的免责声明。*

---

## 📖 完整文档

为了帮助您更好地使用和理解 MediPilot，我们提供了详细的文档：

### 用户文档
- **[用户使用手册](docs/USER_GUIDE.md)** - 完整的安装、配置和使用指南
  - 系统要求与安装步骤
  - 详细配置说明
  - 使用流程与典型场景
  - 常见问题与故障排除

### 开发者文档
- **[开发者文档](docs/DEVELOPMENT.md)** - 深入的架构解析和开发指南
  - 项目架构深度解析
  - 代码审查报告
  - 核心模块详解
  - 扩展开发指南
  - 测试与调试技巧
  - 性能优化建议

### API文档
- **[API参考文档](docs/API_REFERENCE.md)** - 完整的API接口说明
  - 所有类和方法的详细说明
  - 参数和返回值规范
  - 代码示例
  - 数据结构定义

---

## 🎯 快速链接

- **问题反馈**：[GitHub Issues](https://github.com/zetian-jia/MediPilot/issues)
- **功能建议**：[GitHub Discussions](https://github.com/zetian-jia/MediPilot/discussions)
- **贡献指南**：参见 [开发者文档](docs/DEVELOPMENT.md#贡献指南)

---

## 📂 开发者优化说明

作为资深生物信息学程序员，我对本项目进行了以下关键重构：

1. **增加审计追踪**：所有操作均记录至 `logs/` 目录，符合医疗信息化基本要求
2. **强化隐私层**：高斯模糊内核提升，确保病人信息不出内网
3. **语义对齐优化**：Prompt 中加入了临床检验常用的单位对齐与异常标志处理逻辑
4. **中文全面注释**：方便临床科室技术人员维护与理解
5. **完善文档体系**：创建详细的用户手册、开发者文档和API参考

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！请参阅 [开发者文档](docs/DEVELOPMENT.md#贡献指南) 了解详细的贡献流程。

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 📧 联系方式

- **项目维护者**：Zetian Jia
- **GitHub**：https://github.com/zetian-jia/MediPilot
- **问题反馈**：https://github.com/zetian-jia/MediPilot/issues

---

**最后更新**：2026-01-08
