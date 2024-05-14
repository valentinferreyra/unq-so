from math import floor
import itertools
from hardware import HARDWARE

from scheduler import Scheduler

class PriorityQueueScheduler(Scheduler):
    def __init__(self, max_priority = 5):
        if max_priority < 3:
            raise ValueError("Priority Queue Scheduler must have at least 3 priorities")
        
        self._priority_map = self.setup_priority_map(max_priority)
        self._MAX_PRIORITY = max_priority

    def setup_priority_map(self, max_priority):
        return {i: [] for i in range(max_priority)}

    @property
    def name(self):
        return "Priority Queue Scheduler"

    @property
    def getReadyQueue(self):
        return list(itertools.chain(*self._priority_map.values()))

    def tick(self):
        if HARDWARE.clock.currentTick % 10 == 0:
            self._updatePriorities()

    def _updatePriorities(self):
        self._priority_map[0] = self._priority_map.get(0, []) + self._priority_map.get(1, [])
        for priority in range(1, self._MAX_PRIORITY):
            self._priority_map[priority] = self._priority_map.get(priority+1, [])

    def add(self, pcb):
        self._priority_map[pcb.priority].append(pcb)

    def pop(self):
        for priority in range(0, self._MAX_PRIORITY):
            if len(self._priority_map[priority]) > 0:
                return self._priority_map[priority].pop(0)

    def isEmpty(self):
        return all([len(self._priority_map[range]) == 0 for range in range(self._MAX_PRIORITY)])

    def mustExpropiate(self, pcbInCPU, pcbToAdd):
        return False
    
    def isValidPriority(self, priority):
        return 0 <= priority < self._MAX_PRIORITY



class priorityQueueSchedulerPreemptive(PriorityQueueScheduler):

    def mustExpropiate(self, pcbInCPU, pcbToAdd):
        return pcbInCPU.priority > pcbToAdd.priority

    @property
    def name(self):
        return super().name + " Preemptive"

class priorityQueueSchedulerNonPreemptive(PriorityQueueScheduler):

    def mustExpropiate(self, pcbInCPU, pcbToAdd):
        return False

    @property
    def name(self):
        return super().name + " Non Preeemptive"