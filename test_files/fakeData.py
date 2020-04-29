import math
from random import gauss
import decimal

Fs = 6
dt = 1/Fs
Fc = 1/24

Days = 7


StopTime = 24*Days

def wave(t):
    t_range = 7 
    avg = 21
    noise_range = 2
    return -(t_range/2)*math.sin(2*math.pi*Fc*t) + avg + (noise_range/2)*gauss(0,1)

#vals = list(frange(0,StopTime-dt,dt))
l = []
for i in range(StopTime*Fs):
    l.append(i*Fs)        
#T = [wave(t) for t in range(0,StopTime-dt,dt)]
#print(l)
out = []
for i in l:
    out.append(wave(i))

for o in out:
   print(o)
   pass
