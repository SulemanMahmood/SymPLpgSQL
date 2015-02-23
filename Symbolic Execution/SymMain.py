from SymbolicExecutor import SymbolicExecutor

proc_name = 'ReadNum2'
TraceFile = '/home/suleman/TraceLog.txt'

Executor = SymbolicExecutor(proc_name, TraceFile)
Executor.run()

