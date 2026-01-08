import mss
import cv2
import numpy as np
from PIL import Image, ImageDraw

class Perception:
    def __init__(self):
        self.sct = mss.mss()

    def capture(self):
        """高频低延迟截屏"""
        monitor = self.sct.monitors[1]
        sct_img = self.sct.grab(monitor)
        return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

    def privacy_filter(self, image):
        """本地 PII 脱敏过滤"""
        cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        # 模拟模糊化左上角病人信息区
        roi = cv_img[0:150, 0:400]
        blurred_roi = cv2.GaussianBlur(roi, (51, 51), 0)
        cv_img[0:150, 0:400] = blurred_roi
        return Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))

    def apply_som_overlay(self, image, grid_size=80):
        """视觉锚点 (Set-of-Mark)"""
        draw = ImageDraw.Draw(image)
        w, h = image.size
        for x in range(0, w, grid_size):
            draw.line([(x, 0), (x, h)], fill=(255, 0, 0, 128), width=1)
            for y in range(0, h, grid_size):
                draw.line([(0, y), (w, y)], fill=(255, 0, 0, 128), width=1)
                col = chr(65 + (x // grid_size) % 26)
                row = y // grid_size
                draw.text((x + 2, y + 2), f"{col}{row}", fill="red")
        return image
