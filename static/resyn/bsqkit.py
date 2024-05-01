import numpy as np

from bqskit import compile 
from bqskit.qis import StateVector 
from bqskit.qis import StateSystem 

in1 = StateVector(np.array([1,0,0,0])) 
out1 = np.array([0,1,-1,0])/np.sqrt(2) 
out1 = StateVector(out1) 
system = StateSystem({in1:out1}) 
c = compile(system, optimization_level=3) 

print(c.gate_counts) 
