#!/usr/bin/env python
from loader import *
from dispatcher import *


## emulates a compiled program
class Program():

    def __init__(self, name, instructions):
        self._name = name
        self._instructions = self.expand(instructions)

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


class KillInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        pcb = self.kernel.switchPCBState(TERMINATED)
        msgEmptyRQ = "Program Finished: {name} ".format(name=pcb.path)
        msgInComingProcces = "Waiting for the next program..."
        self.kernel.run_next_program_or_log(msgInComingProcces, msgEmptyRQ)

class IoInInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        operation = irq.parameters
        pcb = self.kernel.switchPCBState(WAITING)
        self.kernel.runningPCB = None
        self.kernel.ioDeviceController.runOperation(pcb, operation)
        log.logger.info(self.kernel.ioDeviceController)
        msgInComingProcces = "New I/O operation: {operation} from {pcb}".format(operation=operation, pcb=pcb)
        msgEmptyRQ = "Waiting for I/O operation to finish..."
        self.kernel.run_next_program_or_log(msgInComingProcces, msgEmptyRQ)


class IoOutInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        pcb = self.kernel.ioDeviceController.getFinishedPCB()
        self.kernel.try_run(pcb)
        log.logger.info(self.kernel.ioDeviceController)


class NewInterruptionHandler(AbstractInterruptionHandler):

    def execute(self, irq):
        program = irq.parameters
        baseDir = LOADER.load(program)

        pcb = PCB(program.name, baseDir)
        self.kernel.addPCB(pcb)

        self.kernel.try_run(pcb)


# emulates the core of an Operative System
class Kernel():

    def __init__(self):
        ## setup interruption handlers
        killHandler = KillInterruptionHandler(self)
        HARDWARE.interruptVector.register(KILL_INTERRUPTION_TYPE, killHandler)

        ioInHandler = IoInInterruptionHandler(self)
        HARDWARE.interruptVector.register(IO_IN_INTERRUPTION_TYPE, ioInHandler)

        ioOutHandler = IoOutInterruptionHandler(self)
        HARDWARE.interruptVector.register(IO_OUT_INTERRUPTION_TYPE, ioOutHandler)

        newHandler = NewInterruptionHandler(self)
        HARDWARE.interruptVector.register(NEW_INTERRUPTION_TYPE, newHandler)


        ## controls the Hardware's I/O Device
        self._ioDeviceController = IoDeviceController(HARDWARE.ioDevice)

        self.pcbTable = PcbTable()
        self._readyQueue = []

    @property
    def ioDeviceController(self):
        return self._ioDeviceController

    ## emulates a "system call" for programs execution
    def run(self, program):
        newIRQ = IRQ(NEW_INTERRUPTION_TYPE, program)
        HARDWARE.interruptVector.handle(newIRQ)

    @property
    def runningPCB(self):
        return self.pcbTable.getRunningPCB()

    @runningPCB.setter
    def runningPCB(self, pcb):
        self.pcbTable.setRunningPCB(pcb)

    @property
    def readyQueue(self):
        return self._readyQueue

    def addPCB(self, pcb):
        self.pcbTable.add(pcb)
        
    def switchPCBState(self, state):
        pcb = self.runningPCB
        pcb.state = WAITING
        DISPATCHER.save(pcb)
        return pcb

    # tries to run the next program in the ready queue, 
    # logs the string if there are no more programs to run
    def run_next_program_or_log(self, msgLogInComingProcces, msgLogEmptyRQ):
        if len(self.readyQueue) > 0:
            nextPcb = self.readyQueue.pop(0)
            self.pcbTable.setRunningPCB(nextPcb)
            DISPATCHER.load(nextPcb)
            log.logger.info(msgLogInComingProcces)
        else:
            self.runningPCB = None
            log.logger.info(msgLogEmptyRQ)

    def try_run(self, pcb):
        if self.pcbTable.getRunningPCB():
            pcb.state = READY
            self.readyQueue.append(pcb)
        else:
            pcb.state = RUNNING
            DISPATCHER.load(pcb)
            self.pcbTable.setRunningPCB(pcb)
            log.logger.info("\n Executing program: {name}".format(name=pcb.path))
            log.logger.info(HARDWARE)

    def __repr__(self):
        return "Kernel "
