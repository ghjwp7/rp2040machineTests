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

import micropython, uctypes
from array import array
from utime import ticks_us
from machine import freq
# import machine, uctypes, micropython, array, utime, rp2

TIMELR=const(0x4005400C)

def mm(nn, aa):
    b = uctypes.bytearray_at(TIMELR,4)
    for j in range(nn):
        aa[j] = b[0]
        # mm and mp read only the low byte, because:
        # Problem with next line: reads b 4 times
        #aa[j] = (((((b[3]<<8)|b[2])<<8)|b[1])<<8)|b[0]
        # Problem with next line: works ok, but is slow
        #aa[j] = int.from_bytes(b, 'little')
    #print(f'{aa[5]:9x} {aa[6]:9x} {aa[7]:9x} ')
@micropython.native
def mp(nn, aa):
    b = uctypes.bytearray_at(TIMELR,4)
    for j in range(nn):  aa[j] = b[0]

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
    tlo = ptr32(TIMELR)
    for j in range(nn):
        aa[j] = tlo[0]   # tlo[0] = TIMELR register

def runTest(f):
    freq(f);  freq(f)  # Set system frequency
    rr = [];  nn=17
    # Collect sets of readings
    obase = '012345';  order = '431502 051342 514032 024513'
    for c in order:
        aa = array('I', [0,  0,0,0,0,  0,0,0,0,  0,0,0,0,  0,0,0,0])
        if   c=='0':  mm(nn,aa)
        elif c=='1':  mp(nn,aa)
        elif c=='2':  pp(nn,aa)
        elif c=='3':  np(nn,aa)
        elif c=='4':  vp(nn,aa)
        elif c=='5':  vv(nn,aa)
        if   c!= '':  rr.append(aa)

    # Report results
    print(f'\nSystem frequency = {freq()} Hz')#, end='')
  
    for k in obase:
        if k==' ': continue
        tota, nra = 0, 0
        for o, a in zip(order, rr):
            if o==k:
                print(o, end='')
                pt = a[0]
                for t in a[1:]:
                    dt = t-pt if t>=pt else 256+t-pt
                    tota += dt;  nra += 1
                    print(f'{dt:3}', end=''); pt=t
                print()
        av = tota/nra
        tu = ('mm','mp','pp','np','vp','vv')[ord(k)-ord('0')]
        print(f'{tu}: {nra} readings average {av:5.3f} μs each\n')

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
