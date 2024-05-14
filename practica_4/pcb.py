# Los estados posibles de un PCB
from hardware import *

NEW = "NEW"
READY = "READY"
RUNNING = "RUNNING"
WAITING = "WAITING"
TERMINATED = "TERMINATED"


class PCB:

    def __init__(self, path, baseDir, priority=0, instructions=[]):
        self.pid = PID_PROVIDER.getNewPID()
        self.pc = 0
        self.state = NEW
        self.path = path
        self.baseDir = baseDir
        self.priority = priority
        self._age = 0
        self._instructions = instructions

    # overrides the representation method
    def __repr__(self):
        return "PID: {pid}, Path: {path}, Priority: {priority}, State: {state}, BaseDir: {baseDir}, PC: {pc}"\
            .format(pid=self.pid, pc=self.pc, state=self.state, path=self.path, baseDir=self.baseDir, priority=self.priority, age=self.age, instructions=self._instructions)

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        self._age = value

    def getCpuBurst(self, pc):
        burst = 0
        ins = self._instructions[pc]
        for index in range(pc, len(self._instructions)):
            burst = index - pc
            if self._instructions[index] == INSTRUCTION_IO or self._instructions[index] == INSTRUCTION_EXIT:
                break
        return (burst, ins)


class PcbTable:
    
    def __init__(self):
        self._running_pcb = None
        self._pcbTable = {}
    
    def add(self, pcb):
        self._pcbTable[pcb.pid] = pcb
    
    def get(self, pid):
        return self._pcbTable[pid]
    
    def getRunningPCB(self):
        return self._running_pcb
    
    def setRunningPCB(self, pcb):
        self._running_pcb = pcb

class PidProvider:

    def __init__(self):
        self.pid = -1

    def getNewPID(self):
        self.pid += 1
        return self.pid

PID_PROVIDER = PidProvider()
