from datetime import datetime
from functools import reduce

from pcb import *


class GanttDiagram:

    def __init__(self, kernel):
        self._kernel = kernel
        self._diagram = {"Ready Queue": ["RQ"], "tick": ["tick"]}
        self._pcbHistory = set()
        self._readyQueue = []
        self._runningPCB = None

    @property
    def kernel(self):
        return self._kernel

    def update(self, tick_nbr):
        self._readyQueue = self.kernel.scheduler.getReadyQueue
        self._runningPCB = self.kernel.runningPCB

        self.addNewReadyQueueAndTickToDiagram(tick_nbr)

        self.markCurrentBurstIfAnyPCBRunning(tick_nbr)

        self.markReadyQueuePCBs(tick_nbr)
        self.markWaitingIOQueuePCBs()
        self.markTerminatedPCBs()

    def markCurrentBurstIfAnyPCBRunning(self, tickNbr):
        if self._runningPCB:
            self._pcbHistory.add(self._runningPCB)
            if self._runningPCB.path not in self._diagram:
                self.newPcbOnDiagram(self._runningPCB, tickNbr)
            cpuBurst = self._runningPCB.getCpuBurst(HARDWARE.cpu.pc)
            cpuBurstString = str(cpuBurst[0] - 1) if "CPU" == cpuBurst[1] else cpuBurst[1]
            self._diagram[self._runningPCB.path].append(cpuBurstString)

    def addNewReadyQueueAndTickToDiagram(self, tickNbr):
        rq_pids = list(map(lambda pcb: pcb.pid, self._readyQueue))
        self._diagram["Ready Queue"].append('\n'.join(map(lambda pid: "p" + str(pid), rq_pids)))
        self._diagram["tick"].append(str(tickNbr))

    def markReadyQueuePCBs(self, tickNbr):
        for pcb in self._readyQueue:
            self._pcbHistory.add(pcb)
            if pcb.path not in self._diagram:
                self.newPcbOnDiagram(pcb, tickNbr)
            self._diagram[pcb.path].append("*")

    def markTerminatedPCBs(self):
        for pcb in self._pcbHistory:
            if pcb.state == TERMINATED:
                self._diagram[pcb.path].append("-")

    def markWaitingIOQueuePCBs(self):
        for pcb in self.kernel.ioDeviceController.pcbsInIO():
            self._diagram[pcb.path].append("w")

    def newPcbOnDiagram(self, pcb, tick_nbr):
        self._diagram[pcb.path] = ["p"+str(pcb.pid) + ": " +pcb.path] + [" - "] * tick_nbr

    def write_to_txt(self):
        with open("gantt_diagram.txt", 'w') as file:  # Cambiado a modo 'a' (append)
            file.write("Gantt Diagram\n")
            file.write("Timestamp: " + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "\n")
            file.write("Tick: " + str(HARDWARE.clock.currentTick) + "\n")
            file.write("Scheduler: " + self.kernel.scheduler.name + " | " + "TEP: " + str(self.getTEP()) + "\n")
            file.write("\n" + str(self.kernel.memoryManager.gantt()) + "\n")
            self.write_pcb_table(file)
            file.write(tabulate((self._diagram.values()), tablefmt='psql'))

    def write_pcb_table(self, file):
        file.write("\nPCB Table:\n")
        for pcb in sorted(self._pcbHistory, key=lambda pcb: pcb.pid):
            file.write(str(pcb) + "\n")
        file.write("\n")

    def getTEP(self):
        wait_time = reduce(lambda acc, v: acc + v.count('*'), self._diagram.values(), 0)
        return wait_time / len(self._pcbHistory) if len(self._pcbHistory) > 0 else 0
