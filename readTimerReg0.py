# -*- mode: python;  coding: utf-8 -*-  jiw - 3 Jan & 7 Jan 2025
#  RP2040: print some timer registers
import micropython
from array import array
from utime import ticks_us
from machine import mem32, freq

def mtimes():
    a = array('I', [0]*9)
    t0 = ticks_us()
    for j in range(9):
        a[j] = ticks_us()-t0
    return a

def ptimes():
    TIMER_BASE = 0x40054000  # 4.6.5. List of Registers in Datasheet
    TIMELR = TIMER_BASE+12
    a = array('I', [0]*9)
    t0 = mem32[TIMELR]
    for j in range(9):
        a[j] = mem32[TIMELR]-t0
    return a

@micropython.native
def nmtimes():
    a = array('I', [0]*9)
    t0 = ticks_us()
    for j in range(9):
        a[j] = ticks_us()-t0
    return a

@micropython.native
def nptimes():
    TIMER_BASE = 0x40054000  # 4.6.5. List of Registers in Datasheet
    TIMELR = TIMER_BASE+12
    a = array('I', [0]*9)
    t0 = mem32[TIMELR]
    for j in range(9):
        a[j] = mem32[TIMELR]-t0
    return a

@micropython.viper
def vtimes():
    tlo = ptr32(0x4005400C)  # 4.6.5. List of Registers in Datasheet
    a = array('I', [0,0,0, 0,0,0, 0,0,0])
    t0 = tlo[0]
    for j in range(9):
        a[j] = tlo[0]-t0
    return a

def runTest(f):
    for j in (0,0): # Endeavor to set system frequency
        try:
            if f != freq():
                freq(f) # Set system frequency
        except: print(f'Exception when setting {f} Hz system frequency')

    l, p, L, P, u = mtimes(),  ptimes(),  nmtimes(), nptimes(), vtimes()
    Q, q, m, v, M = nptimes(), ptimes(),  mtimes(),  vtimes(),  nmtimes()
    r, R, w, N, n = ptimes(),  nptimes(), vtimes(),  nmtimes(), mtimes()
    O, x, o, s, S = nmtimes(), vtimes(),  mtimes(),  ptimes(),  nptimes()
    print(f'\nSystem frequency = {freq()} Hz', end='')
    for a, l in zip((p,q,r,s, P,Q,R,S, l,m,n,o, L,M,N,O, u,v,w,x),
                    ('\np','q','r','s', '\nP','Q','R','S',
                     '\nl','m','n','o', '\nL','M','N','O', 
                     '\nu','v','w','x')):
        print(l, end='')
        for t in a:  print(f'{t:5}', end='')
        print(f'  {l[-1]} ', end='');  pt=0
        for t in a:
            print(f'{t-pt:3}', end=''); pt=t
        print()

def main():
    speedLimit = 133000000      # Select upper limit
    speedLimit = 200000000      # Select upper limit
    speedLimit = 250000000      # Select upper limit
    underLimit = 125000000      # Select lower limit
    underLimit =  48000000      # Select lower limit
    f0 = freq()                 # Record so we can restore later
    for f in (f0, 100000000, 200000000, 250000000, f0):
        if underLimit <= f <= speedLimit:
            runTest(f)
    for j in (0,0): 
        if freq() != f0:  freq(f0)  # Restore original frequency
    print(f'System frequency = {freq()} Hz')

if __name__ == "__main__":
    main()

