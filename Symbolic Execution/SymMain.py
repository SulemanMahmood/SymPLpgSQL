from SymbolicExecutor import SymbolicExecutor

proc_name = 'Sum'
TraceFile = '/home/suleman/TraceLog.txt'

Executor = SymbolicExecutor(proc_name, TraceFile)
Executor.run()

