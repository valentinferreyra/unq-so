from scheduler import Scheduler


class FirstComeFirstServedScheduler(Scheduler):
    def __init__(self):
        self.readyQueue = []

    @property
    def name(self):
        return "FCFS"

    @property
    def getReadyQueue(self):
        return self.readyQueue

    def isEmpty(self):
        return len(self.readyQueue) == 0

    def add(self, pcb):
        self.readyQueue.append(pcb)

    def pop(self):
        return self.readyQueue.pop(0)