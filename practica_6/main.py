from hardware import *
from PriorityQueueScheduler import *
from RoundRobinScheduler import *
from ShortestJobFirstScheduler import *
from so import *
import log
from memoryManager import *


def seleccionar_scheduler(): 
    def first_come_first_served():
        return FirstComeFirstServedScheduler()
    
    def priority_queue_nonpreemptive():
        return priorityQueueSchedulerNonPreemptive(6)
    
    def priority_queue_preemptive():
        return priorityQueueSchedulerPreemptive(15)
    
    def round_robin():
        return RoundRobinScheduler(3)

    def shortest_job_first_preemptive():
        return shortestJobFirstPreemptive()

    def shortest_job_first_nonpreemptive():
        return shortestJobFirstNonPreemptive()

    schedulers = {
        "1": first_come_first_served,
        "2": priority_queue_nonpreemptive,
        "3": priority_queue_preemptive,
        "4": round_robin,
        "5": shortest_job_first_preemptive,
        "6": shortest_job_first_nonpreemptive
    }
    
    while True:
        print("1. First Come First Served")
        print("2. Priority Queue (Nonpreemptive, Max priority: 5)")
        print("3. Priority Queue (Preemptive, Max priority: 5)")
        print("4. Round Robin (Default quantum: 3)")
        print("5. Shortest Job First (Preemptive)")
        print("6. Shortest Job First (Nonpreemptive)")
        
        choice = input("Ingrese el número correspondiente al algoritmo de scheduling deseado: ")
        
        if choice in schedulers:
            return schedulers[choice]()
        else:
            print("Opción inválida")

  
if __name__ == '__main__':
    log.setupLogger()
    log.logger.info('Starting emulator')

    ## setup our hardware and set memory size to 20 "cells"
    HARDWARE.setup(20)
    HARDWARE.cpu.enable_stats = True
    
    kernel = Kernel(seleccionar_scheduler())
    HARDWARE.switchOn()
    
    # setup para practica 6
    # prg1 = Program("prg1.exe", [ASM.CPU(2), ASM.IO(), ASM.CPU(3), ASM.IO(), ASM.CPU(2)])
    # prg2 = Program("prg2.exe", [ASM.CPU(7)])
    # prg3 = Program("prg3.exe", [ASM.CPU(4), ASM.IO(), ASM.CPU(1)])
    
    # kernel.fileSystem.write("c:/prg1.exe", prg1)
    # kernel.fileSystem.write("c:/prg2.exe", prg2)
    # kernel.fileSystem.write("c:/prg3.exe", prg3)

    # kernel.run("c:/prg1.exe", 0)
    # kernel.run("c:/prg2.exe", 2)
    # kernel.run("c:/prg3.exe", 1)
    
    # setup de pruebas
    prg1 = Program("prg1.exe", [ASM.CPU(4)])
    prg2 = Program("prg2.exe", [ASM.CPU(5)])
    prg3 = Program("prg3.exe", [ASM.CPU(3)])
    prg4 = Program("prg4.exe", [ASM.CPU(3)])
    prg5 = Program("prg5.exe", [ASM.CPU(2)])

    kernel.fileSystem.write("C:/prg1.exe", prg1)
    kernel.fileSystem.write("C:/prg2.exe", prg2)
    kernel.fileSystem.write("C:/prg3.exe", prg3)
    kernel.fileSystem.write("C:/prg4.exe", prg4)
    kernel.fileSystem.write("C:/prg5.exe", prg5)

    
    kernel.run("C:/prg1.exe", 1)
    kernel.run("C:/prg2.exe", 3)
    kernel.run("C:/prg3.exe", 1)
    kernel.run("C:/prg4.exe", 4)

    kernel.crontab.add_job(12, "C:/prg5.exe", 1)
