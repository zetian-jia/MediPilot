from medipilot.perception.screen import Perception
from medipilot.cognition.engine import Brain, Prompts
from medipilot.execution.action import Executor

def main():
    perception = Perception()
    brain = Brain()
    executor = Executor()
    
    task = "从化验单提取 WBC 并录入系统"
    
    while True:
        img = perception.capture()
        img = perception.privacy_filter(img)
        img = perception.apply_som_overlay(img)
        
        plan = brain.call_vision(img, Prompts.operation(task))
        if executor.execute(plan):
            break

if __name__ == "__main__":
    main()
