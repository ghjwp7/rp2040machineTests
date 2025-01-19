# -*- mode: python;  coding: utf-8 -*-  jiw - 31 Dec 2024 / 1 Jan 2025

#  littlePIO-DMAtest -- Run RP2040 DMA test.  Input address is a PIO SM,
#  output address is an array.

#  Process -- Main sets up PIO SM and DMA and starts both.  Then spins
#  for a while, reporting count at intervals.  Then reports array
#  stats, and runs a couple of loops to drain the Rx fifo of words put
#  into it after the DMA count ran out and while stats were printing.

from rp2     import DMA, PIO, StateMachine, asm_pio
from machine import freq
from utime   import ticks_us, sleep_us
import array

@rp2.asm_pio(fifo_join=PIO.JOIN_RX)  # Use both 4-fifos as an 8-fifo
def pioProg0():        # State machine with 6-cycle loop
    set(y, 0)
    mov(x, invert(y))           # Start x at -1
    wrap_target()               # Decrement x thrice per pass
    jmp(x_dec, "1");  label("1")
    jmp(x_dec, "2");  label("2")
    jmp(x_dec, "3");  label("3")
    mov(isr, invert(x)) [1]     # copy ~x to isr & wait 1 ~
    push(noblock)               # Push isr to Rx fifo
    wrap()

def fifoTell(sm, tb):
    print(f'rx_fifo count: {sm.rx_fifo()}')
    k = 0
    while sm.rx_fifo() > 0:
        k += 1
        print(f'{k:2}.  @t+{ticks_us()-tb} us, fifo→ {sm.get()}')

def main():
    nReadings = 200;  smFreq = 2000;  sm_number = 0;  PIOnum = 0
    smSteps = 6                 # sm steps per sm pass
    cyFreq = smFreq/smSteps;  cyPeriod = 1e6*smSteps/smFreq
    smPeriod =  1e6/smFreq
    print(f'System frequency   = {freq():9}')
    print(f'SM  step frequency = {smFreq:9} Hz = {smPeriod:2.0f} us')
    print(f'SM steps per cycle = {smSteps:9}')
    print(f'SM cycle frequency = {cyFreq:9.2f} Hz = {cyPeriod:2.0f} us')
    nomTTime = cyPeriod*nReadings
    smx = StateMachine(sm_number, pioProg0, freq=smFreq)
    # PIOblok is block 0 or block 1.  sm_number is state machine number 
    PIOblok = 0
    # Next line of code from web didn't work - due to being TX not RX DREQ
    #DataRequestIndex = (PIOblok << 3) + sm_number
    DREQ_PIO0_RX0 = 4  # From 2.5.3.1. DREQ Table in Datasheet
    dmx = DMA()        # Make DMA data structure
    dc = dmx.pack_ctrl(size=2,  # Size 2 selects 4-byte words
             inc_write=True, inc_read=False, treq_sel=DREQ_PIO0_RX0)
    wa = array.array('I', [0]*nReadings) # 'I' -> UINT32
    # Put DMA data structure into registers
    dmx.config(read=smx, write=wa, count=nReadings, ctrl=dc, trigger=False)
    print('DMA count=', end='')
    sleep_us(30000)             # Settle for 30 ms
    t0 = ticks_us()             # Get starting time
    smx.active(1)               # Turn on the state machine
    dmx.active(1)               # Turn on the DMA channel
    for j in range(30):         # While DMA runs, report on its progress
        print(f' {dmx.count}', end='')
        sleep_us(30000)
        if dmx.count == 0: break
    t3 = ticks_us()
    print(f'\nAt t={t3-t0} us after {nReadings} readings in {nomTTime:2.0f} us nominal time --')
    print(f'first,last= {wa[0]}  {wa[-1]}      Delta {wa[-1]-wa[0]}')
    print(f'min: {min(wa)}    avg: {sum(wa)/len(wa):2.2f}    max: {max(wa)}')
    fifoTell(smx,t3)
    dmx.active(0)               # Turn off the DMA
    sleep_us(101000)
    fifoTell(smx,t3)
    smx.active(0)               # Turn off the state machine
    fifoTell(smx,t3)
    return wa

if __name__ == "__main__":
    wa = main()
