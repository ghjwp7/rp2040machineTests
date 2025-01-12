# -*- mode: python;  coding: utf-8 -*-  jiw - 3 Jan & 7 Jan 2025
#  RP2040: print some timer registers

''' Problem atm --  
Traceback (most recent call last):
  File "<stdin>", line 35, in v2
ViperTypeError: return expected 'object' but got 'int'
>>> 
Line 35 is `return a` in v2.

'''

# readTimerReg1.py is derived from readTimerReg2.py by removing 4 of 5
# modes, leaving only the viper mode; but with several versions of
# vtimes, and different ways of specifying how many readings per
# test. Future: have different array sizes

import micropython
from array import array
from utime import ticks_us
from machine import freq

@micropython.viper
def v0():
    tlo = ptr32(0x4005400C)
    a = array('I', [0,  0,0,0,0,  0,0,0,0,  0,0,0,0,  0,0,0,0])
    for j in range(17):
        a[j] = tlo[0]
    return a

@micropython.viper
def v1(nn:int):  # Ref: See timer registers list in Datasheet, 4.6.5.
    tlo = ptr32(0x4005400C) 
    a = array('I', [0,  0,0,0,0,  0,0,0,0,  0,0,0,0,  0,0,0,0])
    for j in range(nn):
        a[j] = tlo[0]
    return a

@micropython.viper
def v2(nn:int, a:ptr32):
    tlo = ptr32(0x4005400C)
    for j in range(nn):
        a[j] = tlo[0]
    #return a

def runTest(f):
    for j in (0,0): # Endeavor to set system frequency
        try:
            if f != freq():
                freq(f) # Set system frequency
        except: print(f'Exception when setting {f} Hz system frequency')

    r = [];  nn=17
    # Collect sets of readings, in all orderings of 012, 9 times per vt.
    order = '120121021012010210201202102'
    for c in order:
        a = array('I', [0,  0,0,0,0,  0,0,0,0,  0,0,0,0,  0,0,0,0])
        if   c=='0':  r.append(v0())
        elif c=='1':  r.append(v1(nn))
        elif c=='2':  v2(nn, a);  r.append(a)

    # Report results
    print(f'\nSystem frequency = {freq()} Hz')#, end='')
  
    for k in '012':
        tota, nra = 0, 0
        for o, a in zip(order, r):
            if o==k:
                print(o, end='')
                pt = a[0]
                for t in a[1:]:
                    tota += t-pt;  nra += 1
                    print(f'{t-pt:3}', end=''); pt=t
                print()
        av = tota/nra
        print(f'v{k} : {nra} readings average {av:5.3f} μs each')

def main():
    speedLimit = 200000000      # Select upper limit
    speedLimit = 250000000      # Select upper limit
    speedLimit = 133000000      # Select upper limit
    underLimit =  48000000      # Select lower limit
    underLimit = 125000000      # Select lower limit
    f0 = freq()                 # Record so we can restore later
    #for f in (f0, 100000000, 200000000, 250000000, f0):
    for f in (100000000, 200000000, f0):
        if underLimit <= f <= speedLimit:
            runTest(f)
    if freq() != f0:  freq(f0)  # Restore original frequency
    if freq() != f0:  freq(f0)  # Restore original frequency
    print(f'System frequency = {freq()} Hz')

if __name__ == "__main__":
    main()

