# -*- mode: python;  coding: utf-8 -*-  jiw - 18 Jan 2025

#  PIO-DMAtest -- Run Micropython RP2040 DMA test.  Input address is a
#  PIO State Machine's RX, output address is an array.

#  Process -- Main sets up PIO SM and 2 DMA channels (with DMA
#  interrupt handlers and callbacks via DISR class).  After starts SM
#  and first DMA it spins for a while, reporting count changes when
#  they occur.  [Now: reports array stats, and runs a couple of loops
#  to drain the Rx fifo of words put into it after the DMA count ran
#  out and while stats were printing] [Future: cleanup]

from rp2     import DMA, PIO, StateMachine, asm_pio
from machine import freq
from utime   import ticks_us, sleep_us
from uctypes import addressof
import array
import micropython
TIMELR=const(0x4005400C)  # From table 527 in 4.6.5 of Datasheet
DREQ_PIO0_RX0 = const(4)  # From 2.5.3.1. DREQ Table in Datasheet
RRwords=const(4)          # number of words per result record

@rp2.asm_pio(fifo_join=PIO.JOIN_RX)  # Use both 4-fifos as an 8-fifo
def pioProg0():        # State machine with 6-cycle loop
    set(y, 0)
    mov(x, invert(y))           # Start x at -1
    wrap_target()               # Decrement x thrice per pass
    jmp(x_dec, "1");  label("1")
    jmp(x_dec, "2");  label("2")
    jmp(x_dec, "3");  label("3")
    mov(isr, invert(x)) [1]     # copy ~x to isr & wait 1 ~
    # If fifo's full, a noblock push = no-op that loses newest value
    push(noblock)               # Push newest value to Rx fifo
    wrap()

def fifoTell(sm, tb):    # Empty RX fifo while reporting contents
    print(f'rx_fifo count: {sm.rx_fifo()}')
    k = 0
    while sm.rx_fifo() > 0:
        k += 1
        print(f'{k:2}.  @t+{ticks_us()-tb} us, fifo→ {sm.get()}')
#-------------------------------------------------------------------
class DISR():        # Class that incorporates DMA & interrupt handler
    def __init__(self, it, eo):
        self.eo  = eo           # even or odd (first or second) DMA
        self.dms = DMA()        # Make DMA data structure in dms
        self.it  = it           # nominal initial time
        self.rri = self.rro = 0 # Results-record indices, in & out
        # Make rr array to track up to 3 result records
        self.rr = array.array('I', [0]*3*RRwords)
        # Allocate reference CBref to callback function ISRCB
        self.CBref= self.ISRCB # to avoid allocation during dmaHISR
        
    # At interrupt, save clock reading, and schedule a callback
    @micropython.viper
    def dmaHISR(self, t):    # Interrupt service for DMA IRQ
        # Get approx time of interrupt; send to callback handler
        micropython.schedule(self.CBref, ticks_us())

    def setup(self, ra, incr, wa, incw, siz, ntran, treq, other):
        ds = self.dms;   eo=self.eo
        dt = other.dms
        # dmaHISR is an ISR, not a callback - actually handles interrupt
        ds.irq(self.dmaHISR, hard=True) # Set up interrupt service
        self.ntran = ntran       # Number of transfers
        s2 = self.siz2 = 2**siz  # Number of bytes per transfer
        self.bytes1Buf = s2 * ntran  # Number of bytes in 1 buffer
        # For each DMA, we have 2 copies of ntran items of s2 bytes each
        self.aw = addressof(wa)+2*ntran*s2*eo # byte-address to write at
        # Pack fields of control word with quiet off to allow interrupt
        dc = ds.pack_ctrl(size=2,   chain_to=dt.channel,
            inc_write=True, inc_read=False, treq_sel=DREQ_PIO0_RX0,
            irq_quiet=False)
        ds.read  = ra  # See p.220 in micropython-docs.pdf for DMA class ref  
        ds.write = self.aw  # See 2.5.7 of Datasheet for DMA registers list
        ds.count = ntran
        self.ctrl  = dc     # Save ctrl for later, when we need it
        ds.active(0)        # Turn off DMA channel

    @micropython.native
    def checkRR(self):
        tc = ticks_us()
        while self.rri > self.rro:
            ds, r, ro, t = self.dms,  self.rr,  self.rro,  self.it 
            os = r[ro+2] - self.aw
            print(f'd{self.eo}c{ds.channel} {r[ro]-t:>8}  {r[ro+1]-r[ro]:>8}  {tc-r[ro]:>8}    {r[ro+2]:08x} {os:4} {r[ro+3]:>6}')
            self.rro += RRwords

    # In callback, save times & value.  Set up for next DMA run, or stop
    @micropython.native
    def ISRCB(self, tus):
        u = ticks_us()          # Get callback time
        r, s, ds = self.rr, self.rri, self.dms
        r[s+0] = tus            # Save ISR time
        r[s+1] = u              # Save callback time
        r[s+2] = self.dms.write # Copy write-address as of now
        r[s+3] = ds.count       # Copy transfer-count as of now
        if self.rri < 2*RRwords:
            self.rri += RRwords
            # Alternate writing between this DMA's first & second buffers
            if s%(2*RRwords) > 0:
                ds.write = self.aw + self.bytes1Buf
            else:
                ds.write = self.aw
            ds.count = self.ntran
        else:
            ds.count = 0
            ds.active(0)        # Turn off this DMA channel

#-------------------------------------------------------------------
def checkBuffer(nbuf, ww, nw): # Count number of ok steps (delta = 3)
    buf = ww[nbuf*nw : (1+nbuf)*nw] # Get buffer to check
    print(f'{nbuf=}  Start: {buf[0]:>4}  Range: {min(buf):>4}-{max(buf):<4} ', end='')
    # Count the number of 3-unit steps in buffer
    n3=0;  vp = buf[0];  not3=[]
    for j in range(1, nw):
        if buf[j]==3+vp:  n3 += 1
        else:  not3.append(vp if vp==buf[j] else (vp,buf[j]))
        vp = buf[j]
    print(f'   ok steps: {n3:>3}', end='')
    if len(not3)>0:
        print(f'  Suspect: {not3[:5]}{"..." if len(not3)>5 else ""}')
    else: print()
#-------------------------------------------------------------------
def main():
    micropython.alloc_emergency_exception_buf(100)

    nReadings = 128;  smFreq = 2000;  sm_number = 0;  PIOnum = 0
    smSteps = 6                 # sm steps per sm pass
    cyFreq = smFreq/smSteps;  cyPeriod = 1e6*smSteps/smFreq
    smPeriod =  1e6/smFreq
    print(f'System frequency   = {freq() :9}')
    print(f'SM  step frequency = {smFreq :9} Hz = {smPeriod:2.0f} us')
    print(f'SM steps per cycle = {smSteps:9}')
    print(f'SM cycle frequency = {cyFreq :9.2f} Hz = {cyPeriod:2.0f} us\n')
    #print('      Interrupt   Callback    Report     Write    aw   Transfer')
    #print('DMA#   time, us   delta us   delta us   Address    +    Count')
    print('      Interrupt   Microseconds to      Write    aw   Transfer')
    print('DMA#   time, us  Callback & Report    Address    +    Count')
    smx = StateMachine(sm_number, pioProg0, freq=smFreq)
    # PIOblok is block 0 or block 1.  sm_number is state machine number 
    PIOblok = 0
    # wa has 2 buffers for each of 2 DMA channels.  2+2 = 4
    wa = array.array('I', [0]*nReadings*4) # 'I' -> UINT32
    postti=10000            # length of sleep for printing to clear
    t0 = ticks_us()+postti  # Nominal starting time
    dmx, dmy = DISR(t0, 0),  DISR(t0, 1)    # Create DMA channels
    for dm, dn in ((dmx, dmy),(dmy,dmx)):   # Set up DMA registers
        #        r@   incRd  w@  incWr siz  ntran=   treq=      other=
        dm.setup(smx, False, wa, True, 2, nReadings, DREQ_PIO0_RX0, dn)
        ds = dm.dms;  os = ds.write - dm.aw
        print(f'd{dm.eo}c{ds.channel} {ds.write:40x} {os:4} {ds.count:>6}')
    sleep_us(postti)            # Let printing finish
    smx.active(1)               # Turn on the state machine
    dmx.dms.active(1)           # Turn on the first DMA channel

    nomTTime = int(cyPeriod*nReadings*4)
    while ticks_us()-t0 < nomTTime+100000:
        dmx.checkRR();   dmy.checkRR()
        if dmx.dms.active() == dmy.dms.active() == 0: break
    t3 = ticks_us()
    smx.active(0)               # Turn off the state machine
    dmx.dms.active(0);  dmy.dms.active(0) # Turn off the DMAs
    print(f'Turned off smx, dmx, dmy at t+{t3-t0} us, vs {nomTTime} nominal')
    sleep_us(10000)
    dmx.checkRR();   dmy.checkRR()
    print()
    for nbuf in range(4): checkBuffer(nbuf, wa, nReadings)
    return wa

if __name__ == "__main__":
    wa = main()
