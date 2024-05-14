from hardware import *
from PriorityQueueScheduler import *
from RoundRobinScheduler import *
from ShortestJobFirstScheduler import *
from so import *
import log


def seleccionar_scheduler(): 
    def first_come_first_served():
        return FirstComeFirstServedScheduler()
    
    def priority_queue_nonpreemptive():
        return priorityQueueSchedulerNonPreemptive(5)
    
    def priority_queue_preemptive():
        return priorityQueueSchedulerPreemptive(5)
    
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

    ## setup our hardware and set memory size to 25 "cells"
    HARDWARE.setup(100)
    HARDWARE.cpu.enable_stats = True

    prg1 = Program("prg1.exe", [ASM.CPU(4), ASM.IO(), ASM.CPU(3), ASM.IO(), ASM.CPU(2)])
    prg2 = Program("prg2.exe", [ASM.CPU(7)])
    prg3 = Program("prg3.exe", [ASM.CPU(4), ASM.IO(), ASM.CPU(1)])

    # pruebas aging
    prg4 = Program("prg4.exe", [ASM.CPU(6), ASM.IO(), ASM.CPU(2), ASM.IO(), ASM.CPU(2),])
    prg5 = Program("prg5.exe", [ASM.CPU(6), ASM.IO(), ASM.CPU(5)])
    prg6 = Program("prg6.exe", [ASM.CPU(4), ASM.IO(), ASM.CPU(6)])


    kernel = Kernel(seleccionar_scheduler())
    HARDWARE.switchOn()

    # execute all programs "concurrently"
    #kernel.run(prg1)
    #kernel.run(prg2)
    #kernel.run(prg3)
    kernel.run(prg4, 1)
    kernel.run(prg6, 10)
    kernel.run(prg5, 4)
