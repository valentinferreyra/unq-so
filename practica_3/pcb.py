# Los estados posibles de un PCB
NEW = "NEW"
READY = "READY"
RUNNING = "RUNNING"
WAITING = "WAITING"
TERMINATED = "TERMINATED"


class PCB:

    def __init__(self, path, baseDir):
        self.pid = PID_PROVIDER.getNewPID()
        self.pc = 0
        self.state = NEW
        self.path = path
        self.baseDir = baseDir

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
