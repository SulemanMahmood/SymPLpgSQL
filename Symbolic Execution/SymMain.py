from SymbolicExecutor import SymbolicExecutor

proc_name = 'Max3'
TraceFile = '/home/suleman/TraceLog.txt'

Executor = SymbolicExecutor(proc_name, TraceFile)
Executor.run()

