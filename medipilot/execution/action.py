import time
import pyautogui

class Executor:
    def __init__(self):
        pyautogui.PAUSE = 0.8
        pyautogui.FAILSAFE = True

    def execute(self, plan):
        action = plan.get("action")
        coord = plan.get("coordinate")
        text = plan.get("text")

        if action == "click":
            pyautogui.moveTo(coord[0], coord[1], duration=0.5)
            pyautogui.click()
        elif action == "type":
            pyautogui.click(coord[0], coord[1])
            pyautogui.write(text, interval=0.1)
        elif action == "finish":
            return True
        return False
