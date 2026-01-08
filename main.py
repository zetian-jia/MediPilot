import time
import sys
from typing import NoReturn
from medipilot.perception.screen import Perception, PerceptionError
from medipilot.cognition.engine import Brain, Prompts, CognitionError
from medipilot.execution.action import Executor, ExecutionError
from medipilot.utils.logger import audit_logger
from configs.settings import config, ConfigError

def show_disclaimer() -> None:
    """
    展示法律免责声明并确认
    
    如果用户不同意，程序将退出
    """
    print("\n" + "=" * 60)
    print(config.DISCLAIMER_TEXT)
    print("=" * 60)
    
    while True:
        confirm = input("\n我已阅读并知悉上述临床风险 (y/n): ").strip().lower()
        if confirm == 'y':
            print("✓ 已确认。继续启动...\n")
            break
        elif confirm == 'n':
            print("程序已退出。")
            sys.exit(0)
        else:
            print("请输入 'y' 或 'n'")

def validate_environment() -> None:
    """
    验证运行环境和配置
    
    Raises:
        ConfigError: 配置验证失败
    """
    try:
        audit_logger.info("正在验证配置...")
        config.validate()
        audit_logger.info("✓ 配置验证通过")
        
        # 显示配置信息
        config.display_info()
        
    except ConfigError as e:
        audit_logger.critical(f"配置验证失败: {e}")
        print(f"\n❌ 配置错误: {e}")
        print("\n请检查 .env 文件并确保所有必需的配置项都已正确设置。")
        print("参考 .env.example 文件获取配置模板。\n")
        sys.exit(1)

def main() -> NoReturn:
    """
    主程序入口
    
    工作流程:
        1. 显示免责声明
        2. 验证配置
        3. 初始化组件
        4. 执行感知-认知-执行循环
    """
    print("\n" + "=" * 60)
    print("🩺 MediPilot - 临床医生 AI 自动化副驾驶")
    print("=" * 60 + "\n")
    
    # 1. 启动展示免责声明 (临床合规要求)
    show_disclaimer()
    
    # 2. 验证配置
    validate_environment()
    
    # 3. 初始化核心组件
    try:
        audit_logger.info("开始初始化核心组件...")
        perception = Perception()
        brain = Brain()
        executor = Executor()
        audit_logger.info("✓ 所有组件初始化完成\n")
        
    except (PerceptionError, CognitionError, ExecutionError) as e:
        audit_logger.critical(f"组件初始化失败: {e}")
        print(f"\n❌ 初始化错误: {e}\n")
        sys.exit(1)
    
    # 4. 定义任务
    task_desc = (
        "从屏幕显示的化验单中提取 WBC, RBC, Hgb, PLT 指标，"
        "并录入到电子病历系统对应的输入框中。"
    )
    
    audit_logger.info("=" * 60)
    audit_logger.info("MediPilot 临床助手开始运行...")
    audit_logger.info(f"任务描述: {task_desc}")
    audit_logger.info("=" * 60)
    
    iteration_count = 0
    max_iterations = 100  # 防止无限循环
    
    try:
        while iteration_count < max_iterations:
            iteration_count += 1
            audit_logger.info(f"\n--- 迭代 #{iteration_count} ---")
            
            # A. 感知阶段
            try:
                img = perception.capture()
                # 执行本地隐私脱敏 (不上传 PII 到云端)
                img = perception.privacy_filter(img)
                # 叠加 SoM 视觉锚点
                img_with_som = perception.apply_som_overlay(img)
            except PerceptionError as e:
                audit_logger.error(f"感知阶段失败: {e}")
                audit_logger.info("等待3秒后重试...")
                time.sleep(3)
                continue
            
            # B. 认知决策阶段
            try:
                # 传入当前任务描述及 SoM 图像
                plan = brain.call_vision(img_with_som, Prompts.operation(task_desc))
            except CognitionError as e:
                audit_logger.error(f"认知阶段失败: {e}")
                audit_logger.info("等待5秒后重试...")
                time.sleep(5)
                continue
            
            # C. 执行阶段
            try:
                is_finished = executor.execute(plan)
                
                if is_finished:
                    audit_logger.info("\n" + "=" * 60)
                    audit_logger.info("✓ 工作流程已成功完成")
                    audit_logger.info(f"总迭代次数: {iteration_count}")
                    audit_logger.info("=" * 60)
                    break
            except ExecutionError as e:
                audit_logger.error(f"执行阶段失败: {e}")
                audit_logger.info("继续下一次迭代...")
                
            # 控制采样频率，避免过度占用系统资源
            time.sleep(config.SCREENSHOT_DELAY)
        
        if iteration_count >= max_iterations:
            audit_logger.warning(f"达到最大迭代次数 ({max_iterations})，程序终止")
            
    except KeyboardInterrupt:
        audit_logger.warning("\n用户手动中止程序 (Ctrl+C)")
        print("\n\n程序已安全退出。")
        
    except Exception as e:
        audit_logger.critical(f"系统遭遇不可恢复错误: {e}", exc_info=True)
        print(f"\n\n❌ 严重错误: {e}")
        print("详细信息已记录到日志文件。\n")
        sys.exit(1)
    
    finally:
        audit_logger.info("MediPilot 已关闭")
        print("\n感谢使用 MediPilot！\n")

if __name__ == "__main__":
    main()
