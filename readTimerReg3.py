# -*- mode: python;  coding: utf-8 -*-  jiw - 3 Jan & 7 Jan 2025
#  RP2040: print some timer registers

# readTimerReg3.py is derived from readTimerReg 1 & 2 by using test
# dispatch as in 1 and test units from 2.  Ie, having an `order`
# string to choose which test unit to call, and having (1) a
# plain-python test unit that calls ticks_us(); (2) like 1, except
# with @micropython.native decorator; (3) like 1, except with
# @micropython.viper decorator, and necessary type declarations; (4) a
# @micropython.viper decorated unit with TIMELR pointer.

# Note, all of the test units here take 2 parameters: nn = test-pass
# count; aa = provided array.  All units modify aa in place, instead
# of creating and returning an array.

import micropython
from array import array
from utime import ticks_us
from machine import freq


def pp(nn, aa):
    for j in range(nn):  aa[j] = ticks_us()

@micropython.native
def np(nn, aa):
    for j in range(nn):  aa[j] = ticks_us()

@micropython.viper
def vp(nn:int, aa:ptr32):
    for j in range(nn):  aa[j] = int(ticks_us())

@micropython.viper
def vv(nn:int, aa:ptr32):
    tlo = ptr32(0x4005400C)
    for j in range(nn):
        aa[j] = tlo[0]   # tlo[0] = TIMELR register

def runTest(f):
    freq(f);  freq(f)  # Set system frequency
    rr = [];  nn=17
    # Collect sets of readings, in several different orderings
    order = '312013210321013320103210230120323102'
    for c in order:
        aa = array('I', [0,  0,0,0,0,  0,0,0,0,  0,0,0,0,  0,0,0,0])
        if   c=='0':  pp(nn,aa)
        elif c=='1':  np(nn,aa)
        elif c=='2':  vp(nn,aa)
        elif c=='3':  vv(nn,aa)
        rr.append(aa)

    # Report results
    print(f'\nSystem frequency = {freq()} Hz')#, end='')
  
    for k in '0123':
        tota, nra = 0, 0
        for o, a in zip(order, rr):
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
    f0 = freq()       # Record freq so we can restore later
    # Choose frequency list via first true condition
    if   0: fl = (100000000, 200000000, f0)
    elif 0: fl = (100000000, 200000000)
    else:   fl = (f0,)

    for f in fl:   runTest(f)   # 

    freq(f0); freq(f0) # Restore original frequency
    print(f'System frequency = {freq()} Hz')

if __name__ == "__main__":
    main()
