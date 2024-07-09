from scheduler import Scheduler
from hardware import *

class RoundRobinScheduler(Scheduler):
    def __init__(self, quantum):
        self.readyQueue = []
        HARDWARE.timer.quantum = quantum
        
    @property
    def getReadyQueue(self):
        return self.readyQueue
    
    def add(self, pcb):
        self.readyQueue.append(pcb)
    
    def pop(self):
        return self.readyQueue.pop(0)
    
    def isEmpty(self):
        return len(self.readyQueue) == 0
    
    def mustExpropiate(self, pcbInCPU, pcbToAdd):
        return False
    
    @property
    def name(self):
        return "Round Robin"
    