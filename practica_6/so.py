#!/usr/bin/env python
from FileSystem import FileSystem
from FirstComeFirstServedScheduler import FirstComeFirstServedScheduler
from GanttDiagram import GanttDiagram
from crontab import Crontab
from loader import *
from dispatcher import *
from memoryManager import *


## emulates a compiled program
class Program():

    def __init__(self, name, instructions, priority=0):
        self._name = name
        self._instructions = self.expand(instructions)
        self._priority = priority

    @property
    def name(self):
        return self._name

    @property
    def instructions(self):
        return self._instructions

    def addInstr(self, instruction):
        self._instructions.append(instruction)

    def expand(self, instructions):
        expanded = []
        for i in instructions:
            if isinstance(i, list):
                ## is a list of instructions
                expanded.extend(i)
            else:
                ## a single instr (a String)
                expanded.append(i)

        ## now test if last instruction is EXIT
        ## if not... add an EXIT as final instruction
        last = expanded[-1]
        if not ASM.isEXIT(last):
            expanded.append(INSTRUCTION_EXIT)

        return expanded

    def __repr__(self):
        return "Program({name}, {instructions})".format(name=self._name, instructions=self._instructions)


## emulates an Input/Output device controller (driver)
class IoDeviceController():

    def __init__(self, device):
        self._device = device
        self._waiting_queue = []
        self._currentPCB = None

    def runOperation(self, pcb, instruction):
        pair = {'pcb': pcb, 'instruction': instruction}
        # append: adds the element at the end of the queue
        self._waiting_queue.append(pair)
        # try to send the instruction to hardware's device (if is idle)
        self.__load_from_waiting_queue_if_apply()

    def getFinishedPCB(self):
        finishedPCB = self._currentPCB
        self._currentPCB = None
        self.__load_from_waiting_queue_if_apply()
        return finishedPCB

    def __load_from_waiting_queue_if_apply(self):
        if (len(self._waiting_queue) > 0) and self._device.is_idle:
            ## pop(): extracts (deletes and return) the first element in queue
            pair = self._waiting_queue.pop(0)
            # print(pair)
            pcb = pair['pcb']
            instruction = pair['instruction']
            self._currentPCB = pcb
            self._device.execute(instruction)

    def pcbsInIO(self):
        waitingPCBs = []
        if self._currentPCB:
            waitingPCBs.append(self._currentPCB)

        for pcb in self._waiting_queue:
            waitingPCBs.append(pcb['pcb'])
        return waitingPCBs

    def __repr__(self):
        return "IoDeviceController for {deviceID} running: {currentPCB} waiting: {waiting_queue}".format(
            deviceID=self._device.deviceId, currentPCB=self._currentPCB, waiting_queue=self._waiting_queue)


## emulates the  Interruptions Handlers
class AbstractInterruptionHandler():
    def __init__(self, kernel):
        self._kernel = kernel

    @property
    def kernel(self):
        return self._kernel

    def execute(self, irq):
        log.logger.error("-- EXECUTE MUST BE OVERRIDEN in class {classname}".format(classname=self.__class__.__name__))

class TimeoutInterruptionHandler(AbstractInterruptionHandler):
        def execute(self, irq):
            if not self.kernel.scheduler.isEmpty():
                pcb = self.kernel.switchPCBState(WAITING)
                self.kernel.scheduler.add(pcb)
                self.kernel.run_next_program_or_log("Program finished by timeout", "Waiting for the next program...")
            else:
                HARDWARE.timer.reset()
    

class KillInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        pcb = self.kernel.switchPCBState(TERMINATED)
        msgEmptyRQ = "Program Finished: {name} ".format(name=pcb.path)
        msgInComingProcces = "Waiting for the next program..."
        self.kernel.run_next_program_or_log(msgInComingProcces, msgEmptyRQ)
        log.logger.info(self.kernel.memoryManager)
        self.kernel.memoryManager.freeFrames(pcb.page_table)
        log.logger.info(self.kernel.memoryManager)


class IoInInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        operation = irq.parameters
        pcb = self.kernel.switchPCBState(WAITING)
        self.kernel.runningPCB = None
        self.kernel.ioDeviceController.runOperation(pcb, operation)
        log.logger.error(self.kernel.ioDeviceController)
        msgInComingProcces = "New I/O operation: {operation} from {pcb}".format(operation=operation, pcb=pcb)
        msgEmptyRQ = "Waiting for I/O operation to finish..."

        self.kernel.run_next_program_or_log(msgInComingProcces, msgEmptyRQ)


class IoOutInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        pcb = self.kernel.ioDeviceController.getFinishedPCB()
        self.kernel.try_run(pcb)
        log.logger.debug(self.kernel.ioDeviceController)


class NewInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        program = irq.parameters['program']
        priority = irq.parameters['priority']
        pcb = PCB(program.name, priority= priority, instructions= program.instructions)
        log.logger.info(self.kernel.memoryManager)

        isInMemory = LOADER.load(pcb)

        if isInMemory:
            log.logger.info(self.kernel.memoryManager)
            self.kernel.addPCB(pcb)
            self.kernel.try_run(pcb)
            log.logger.info(HARDWARE)

class StatsInterruptionHandler(AbstractInterruptionHandler):

    def __init__(self, irq):
        super(StatsInterruptionHandler, self).__init__(irq)
        self._gantt = GanttDiagram(self.kernel)

    @property
    def gantt(self):
        return self._gantt

    def execute(self, irq):
        self.kernel.scheduler.tick()
        self.printGandIf()
        self.gantt.update(HARDWARE.clock.currentTick)

    def printGandIf(self):
        if HARDWARE.clock.currentTick > 0:
            self.gantt.write_to_txt()


# emulates the core of an Operative System
class Kernel():

    def __init__(self, scheduler=FirstComeFirstServedScheduler()):

        ## controls the Hardware's I/O Device


        self.pcbTable = PcbTable()
        self._scheduler = scheduler
        HARDWARE.mmu.frameSize = 4
        self._memoryManager = MemoryManager(self)
        self._fileSystem = FileSystem()

        ## setup interruption handlers
        killHandler = KillInterruptionHandler(self)
        HARDWARE.interruptVector.register(KILL_INTERRUPTION_TYPE, killHandler)

        ioInHandler = IoInInterruptionHandler(self)
        HARDWARE.interruptVector.register(IO_IN_INTERRUPTION_TYPE, ioInHandler)

        ioOutHandler = IoOutInterruptionHandler(self)
        HARDWARE.interruptVector.register(IO_OUT_INTERRUPTION_TYPE, ioOutHandler)

        newHandler = NewInterruptionHandler(self)
        HARDWARE.interruptVector.register(NEW_INTERRUPTION_TYPE, newHandler)

        statsHandler = StatsInterruptionHandler(self)
        HARDWARE.interruptVector.register(STAT_INTERRUPTION_TYPE, statsHandler)
        
        timeOutHandler = TimeoutInterruptionHandler(self)
        HARDWARE.interruptVector.register(TIMEOUT_INTERRUPTION_TYPE, timeOutHandler)

        self._ioDeviceController = IoDeviceController(HARDWARE.ioDevice)
        self._crontab = Crontab(self)
        self._crontab = Crontab(self)

        LOADER.kernel = self

    @property
    def fileSystem(self):
        return self._fileSystem

    @property
    def cronTable(self):
        return self._crontab

    @property
    def memoryManager(self):
        return self._memoryManager

    @property
    def crontab(self):
        return self._crontab

    @property
    def ioDeviceController(self):
        return self._ioDeviceController

    ## emulates a "system call" for programs execution
    def run(self, path, priority = 0):
        if not self.scheduler.isValidPriority(priority):
            return log.logger.critical("Invalid priority: {priority}".format(priority=priority))
        newIRQ = IRQ(NEW_INTERRUPTION_TYPE, {'program': self.fileSystem.read(path), 'priority': priority})
        HARDWARE.interruptVector.handle(newIRQ)

    @property
    def runningPCB(self):
        return self.pcbTable.getRunningPCB()

    @runningPCB.setter
    def runningPCB(self, pcb):
        self.pcbTable.setRunningPCB(pcb)

    @property
    def scheduler(self):
        return self._scheduler

    def addPCB(self, pcb):
        self.pcbTable.add(pcb)
        
    def switchPCBState(self, state):
        pcb = self.runningPCB
        pcb.state = state
        DISPATCHER.save(pcb)
        return pcb

    # tries to run the next program in the ready queue, 
    # logs the string if there are no more programs to run
    def run_next_program_or_log(self, msgLogInComingProcces, msgLogEmptyRQ):
        if not self.scheduler.isEmpty():
            self.loadAndRun(self.scheduler.pop())
            log.logger.debug(msgLogInComingProcces)
        else:
            self.runningPCB = None
            log.logger.debug(msgLogEmptyRQ)

    def try_run(self, pcb):
        if self.pcbTable.getRunningPCB():
            self.expropriate_if_possible_or_add_to_readyQueue(pcb)
        else:
            self.loadAndRun(pcb)

    def loadAndRun(self, pcb):
        self.pcbTable.setRunningPCB(pcb)
        pcb.state = RUNNING
        DISPATCHER.load(pcb)
        log.logger.critical("Executing program: {pcb}".format(pcb=pcb))

    def expropriate_if_possible_or_add_to_readyQueue(self, pcb):
        if self.scheduler.mustExpropiate(self.runningPCB, pcb):
            pcbToExpropiate = self.switchPCBState(WAITING)
            self.scheduler.add(pcbToExpropiate)
            log.logger.warning("Expropiating PCB: {pcb}".format(pcb=pcbToExpropiate))
            pcb.state = RUNNING
            DISPATCHER.load(pcb)
            self.pcbTable.setRunningPCB(pcb)
            log.logger.critical("Loading program: {pcb}".format(pcb=pcb))
        else:
            pcb.state = READY
            self.scheduler.add(pcb)
            
    def __repr__(self):
        return "Kernel "
