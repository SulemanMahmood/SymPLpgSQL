from SymbolicExecutor import SymbolicExecutor

proc_name = 'InsertTest'
TraceFile = '/home/suleman/TraceLog.txt'

Executor = SymbolicExecutor(proc_name, TraceFile)
Executor.run()

