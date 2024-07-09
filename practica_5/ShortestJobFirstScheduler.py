from scheduler import Scheduler
from hardware import HARDWARE

class shortestJobFirstScheduler(Scheduler):
    def __init__(self):
        self.readyQueue = []

    @property
    def name(self):
        return "Shortest Job First"

    @property
    def getReadyQueue(self):
        return self.readyQueue

    def add(self, pcb):
        self.readyQueue.append(pcb)
        self.readyQueue.sort(key=lambda x: self.sortByCpuBurst(x), reverse=False)


    def sortByCpuBurst(self, pcb):
        priority = pcb.getCpuBurst(pcb.pc)[0]
        return priority


    def pop(self):
        pcb = self.readyQueue.pop(0)
        return pcb

    def isEmpty(self):
        return len(self.readyQueue) == 0

    def mustExpropiate(self, pcbInCPU, pcbToAdd):
        return False

class shortestJobFirstPreemptive(shortestJobFirstScheduler):

        def mustExpropiate(self, pcbInCPU, pcbToAdd):
            return pcbInCPU.getCpuBurst(HARDWARE.cpu.pc)[0] > pcbToAdd.getCpuBurst(pcbToAdd.pc)[0]

        @property
        def name(self):
            return super().name + " Preemptive"

class shortestJobFirstNonPreemptive(shortestJobFirstScheduler):

        def mustExpropiate(self, pcbInCPU, pcbToAdd):
            return False

        @property
        def name(self):
            return super().name + " Non Preemptive"