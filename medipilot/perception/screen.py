import mss
import cv2
import numpy as np
from typing import Optional
from PIL import Image, ImageDraw
from configs.settings import config
from medipilot.utils.logger import audit_logger

class PerceptionError(Exception):
    """感知层异常"""
    pass

class Perception:
    """
    感知层：负责环境"观察"与隐私处理
    
    Attributes:
        sct: MSS截屏对象
    """
    
    def __init__(self) -> None:
        """初始化感知层，创建截屏实例"""
        try:
            self.sct = mss.mss()
            audit_logger.info("感知模块初始化完成")
        except Exception as e:
            audit_logger.critical(f"感知模块初始化失败: {e}")
            raise PerceptionError(f"无法初始化截屏模块: {e}")

    def capture(self) -> Image.Image:
        """
        高频低延迟截屏
        
        Returns:
            PIL.Image.Image: RGB格式的原始截图对象
            
        Raises:
            PerceptionError: 截屏失败时抛出
        """
        try:
            monitor = self.sct.monitors[1]
            sct_img = self.sct.grab(monitor)
            # 转换为 RGB 格式供后续处理
            image = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            audit_logger.debug(f"截屏成功，尺寸: {image.size}")
            return image
        except Exception as e:
            audit_logger.error(f"截屏失败: {e}")
            raise PerceptionError(f"屏幕捕获失败: {e}")

    def privacy_filter(self, image: Image.Image) -> Image.Image:
        """
        本地 PII (个人身份信息) 脱敏过滤
        
        功能:
            根据配置文件的 PRIVACY_REGION，对病人敏感信息区域进行高斯模糊。
            确保敏感数据在发送给大模型 API 前已在本地完成脱敏。
        
        Args:
            image: 原始截图
            
        Returns:
            PIL.Image.Image: 脱敏后的截图
            
        Raises:
            PerceptionError: 图像处理失败时抛出
        """
        try:
            cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # 从配置获取隐私保护区域 [y1, y2, x1, x2]
            y1, y2, x1, x2 = config.PRIVACY_REGION
            
            # 验证区域有效性
            height, width = cv_img.shape[:2]
            if y2 > height or x2 > width:
                audit_logger.warning(
                    f"隐私区域 {config.PRIVACY_REGION} 超出图像边界 ({width}x{height})，"
                    "将调整为图像范围内"
                )
                y2 = min(y2, height)
                x2 = min(x2, width)
            
            # 执行高斯模糊
            roi = cv_img[y1:y2, x1:x2]
            if roi.size > 0:  # 确保ROI非空
                blurred_roi = cv2.GaussianBlur(roi, (99, 99), 30)  # 增强模糊程度
                cv_img[y1:y2, x1:x2] = blurred_roi
                audit_logger.debug(f"已应用隐私过滤: 区域 {config.PRIVACY_REGION}")
            else:
                audit_logger.warning(f"隐私区域为空，跳过模糊处理")
            
            return Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
            
        except Exception as e:
            audit_logger.error(f"隐私过滤失败: {e}")
            # 即使失败也返回原图，但记录错误
            audit_logger.warning("⚠️  隐私过滤失败，返回原始图像。请检查配置！")
            return image

    def apply_som_overlay(self, image: Image.Image, grid_size: int = 80) -> Image.Image:
        """
        视觉锚点叠加 (Set-of-Mark)
        
        功能:
            在图像上绘制红色网格并标注坐标 (如 A1, B2)，
            协助大模型理解 UI 元素的相对位置。
            
        Args:
            image: 待处理图像
            grid_size: 网格大小（像素），默认80
            
        Returns:
            PIL.Image.Image: 带有网格标注的图像
            
        Raises:
            PerceptionError: 网格绘制失败时抛出
        """
        try:
            # 验证grid_size
            if grid_size <= 0 or grid_size > 1000:
                audit_logger.warning(
                    f"网格大小 {grid_size} 超出合理范围 (1-1000)，使用默认值 80"
                )
                grid_size = 80
            
            # 创建图像副本以避免修改原图
            image = image.copy()
            draw = ImageDraw.Draw(image)
            w, h = image.size
            
            # 绘制网格线
            for x in range(0, w, grid_size):
                draw.line([(x, 0), (x, h)], fill=(255, 0, 0, 100), width=1)
            for y in range(0, h, grid_size):
                draw.line([(0, y), (w, y)], fill=(255, 0, 0, 100), width=1)
                
            # 标注坐标文字
            for x in range(0, w, grid_size):
                for y in range(0, h, grid_size):
                    col_idx = x // grid_size
                    row_idx = y // grid_size
                    # 生成 A0, B1 风格的标签
                    col_label = ""
                    temp_idx = col_idx
                    while temp_idx >= 0:
                        col_label = chr(65 + (temp_idx % 26)) + col_label
                        temp_idx = (temp_idx // 26) - 1
                    
                    label = f"{col_label}{row_idx}"
                    draw.text((x + 2, y + 2), label, fill="red")
            
            audit_logger.debug(f"SoM网格叠加完成，网格大小: {grid_size}px")
            return image
            
        except Exception as e:
            audit_logger.error(f"SoM网格绘制失败: {e}")
            raise PerceptionError(f"无法绘制视觉网格: {e}")
