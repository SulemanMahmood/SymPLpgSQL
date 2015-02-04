from SymbolicExecutor import SymbolicExecutor

proc_name = 'Max3'
TraceFile = '/home/suleman/TraceLog.txt'
procDetailFile = './Resources/'+proc_name+'Details.txt'

Executor = SymbolicExecutor(proc_name, procDetailFile, TraceFile)
Executor.run()

