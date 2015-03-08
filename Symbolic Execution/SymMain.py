from SymbolicExecutor import SymbolicExecutor

proc_name = 'JoinTest'
TraceFile = '/home/suleman/TraceLog.txt'

Executor = SymbolicExecutor(proc_name, TraceFile)
Executor.run()

