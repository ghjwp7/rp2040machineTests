# -*- mode: python;  coding: utf-8 -*-  jiw - 18 Jan 2025

#  PIO-DMAtest -- Run Micropython RP2040 DMA test.  Input address is a
#  PIO State Machine's RX, output addresses are arrays.

#  Main sets up PIO SM and some DMA channels, then lets them run to
#  fill each buffer several times, then shuts down.  DMA channels
#  chain in a loop; eg 0->1->2->0 if there are 3 channels.  DISR class
#  supports DMA-completion-interrupt handlers and callbacks.  At each
#  interrupt, handler saves a timer reading and schedules a callback.
#  The callback runs a fraction of a millisecond after the interrupt
#  handler calls the scheduler.  It stores the interrupt time and its
#  own time in a records array.  Meanwhile, the main thread spins in a
#  loop, calling checkRR() to check for and report changes when they
#  occur.  

from rp2     import DMA, PIO, StateMachine, asm_pio
from machine import freq
from utime   import ticks_us, sleep_us
from uctypes import addressof
import array
import micropython
TIMELR=const(0x4005400C)  # From table 527 in 4.6.5 of Datasheet
DREQ_PIO0_RX0 = const(4)  # From 2.5.3.1. DREQ Table in Datasheet
RRwords=const(2)          # number of words per result record
RRsets=const(5)           # number of result records per DMA
BufWords=const(64)        # number of words per work buffer
SizCode=const(2)          # s=0/1/2 for 2^s bytes per transfer
nDMA=const(3)             # number of DMA's to run
SMFreq=const(150000)        # Base frequency for PIO State Machine
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
class DISR():   # Class that incorporates DMA & interrupt handler
    def __init__(self, it, ix):
        self.dms = ds = DMA()   # Get channel & make data structure
        ds.active(0)            # Turn off DMA channel
        self.ix  = ix           # index in daa list
        self.it  = it           # nominal initial time
        self.rri = self.rro = 0 # Results-record indices, in & out
        # Make rr array to track up to RRsets result records
        self.rr = array.array('I', [0]*(1+RRsets)*RRwords)
        # Make wa work array to record data from PIO
        self.wa = array.array('I', [0]*BufWords)
        # Allocate reference CBref to callback function ISRCB...
        self.CBref= self.ISRCB  # ...avoiding allocation during ISR

    # At interrupt, read clock and schedule callback
    @micropython.viper
    def dmaHISR(self, t):    # Interrupt service for DMA IRQ
        # Get approx time of interrupt; send to callback handler
        micropython.schedule(self.CBref, ticks_us())

    def setup(self, rat, incr, incw, treq, chainee):
        # Params: read address; read-incr flag; write-incr flag;
        # source of DREQ; and DMA to chain to.
        ds = self.dms
        # dmaHISR is an ISR, not a callback - actually handles interrupt
        ds.irq(self.dmaHISR, hard=True) # Set up interrupt service
        s2 = self.siz2 = 2**SizCode     # Number of bytes per transfer
        self.bytes1Buf = s2 * BufWords  # Number of bytes in 1 buffer
        self.aw = addressof(self.wa)    # byte-address to write at
        ds.read  = rat    # See p.220 in micropython-docs.pdf for DMA class  
        ds.write = self.aw  # See 2.5.7 of Datasheet for DMA registers list
        ds.count = BufWords
        # Pack control word & save for later, when we need it
        self.ctrl = ds.pack_ctrl(size=SizCode,  treq_sel=DREQ_PIO0_RX0,
            inc_read=False,   chain_to=chainee.dms.channel,
            inc_write=True,   irq_quiet=False)
        ds.active(0)        # Turn off DMA channel
        ds.ctrl = self.ctrl
        ds.active(0)        # Turn off DMA channel

    @micropython.native
    def checkBuffer(self):  # Count number of ok steps in buffer
        ww = self.wa;    n3=0;    vp = ww[0];
        # Count the number of 3-unit steps in buffer
        for j in range(1, BufWords):
            if ww[j]==3+vp:
                n3 += 1
            vp = ww[j]
        print(f'  {ww[0]:>9}  {min(ww):>4}-{max(ww):<4}  {n3:>3}')

    @micropython.native
    def checkRR(self):
        te = ticks_us()
        while self.rro < self.rri:
            ds, r, ro, it = self.dms,  self.rr,  self.rro,  self.it 
            ti = r[ro]-it;   tcb = r[ro+1]-r[ro];   tck=te-r[ro]
            # Print time-in-program and times since interrupt
            print(f'{ro:2}  {ds.channel}  {ti:>9} {tcb:>7} {tck:>8}', end='')
            self.checkBuffer()
            self.rro += RRwords

    # In callback, save times & value.  Set up for next DMA run, or stop
    @micropython.native
    def ISRCB(self, tus):
        u = ticks_us()          # Get callback time
        r, s, ds = self.rr, self.rri, self.dms
        r[s+0] = tus            # Save ISR time
        r[s+1] = u              # Save callback time
        ds.write = self.aw      # Reset the output address
        if self.rri <= (RRsets-1)*RRwords:
            self.rri += RRwords
            ds.count = BufWords
        else:
            ds.active(0)        # Turn off this DMA channel
            ds.count = 0

#-------------------------------------------------------------------
#-------------------------------------------------------------------
def main():
    # In case of exception while handling an interrupt:
    micropython.alloc_emergency_exception_buf(100)

    sm_number = 0;  PIOnum = 0
    smSteps = 6                 # sm steps per sm pass
    cyFreq = SMFreq/smSteps;  cyPeriod = 1e6*smSteps/SMFreq
    smPeriod =  1e6/SMFreq
    print(f'System frequency   = {freq() :9}')
    print(f'SM  step frequency = {SMFreq :9} Hz = {smPeriod:2.0f} us')
    print(f'SM steps per cycle = {smSteps:9}')
    print(f'SM cycle frequency = {cyFreq :9.2f} Hz = {cyPeriod:2.0f} us')
    nomTTime = int(cyPeriod*BufWords*RRsets*nDMA)
    print(f'Data collects during next {nomTTime} us, w/progress notes\n')
    print('        Interrupt   Microseconds to    First    Range     OK')
    print('rr DMA#  time, us  Callback & Report   value   min-max   steps')
    smx = StateMachine(sm_number, pioProg0, freq=SMFreq)
    # PIOblok is block 0 or block 1.  sm_number is state machine number 
    PIOblok = 0
    postti=10000            # length of sleep for printing to clear
    t0 = ticks_us()+postti  # Nominal starting time
    daa = []
    #============Setup DMA channels, with DISRs for IRQs========
    for ix in range(nDMA):    # Make list of DMA channels
        daa.append(DISR(t0, ix))
    # Finish setting up DMA channels, including chain-to's
    for dm in daa:   # Set up DMA registers
        chainee = daa[(1+dm.ix)%nDMA] # Find channel to chain to
        #        r@   incRd  incWr  treq=          other=
        dm.setup(smx, False, True,  DREQ_PIO0_RX0, chainee)
        ds = dm.dms             # ds = DMA data structure
    sleep_us(postti)            # Let printing finish
    smx.active(1)               # Turn on the state machine
    daa[0].dms.active(1)        # Turn on a first DMA channel
    #============Get & analyze expected readings=================
    while ticks_us()-t0 < nomTTime+100000: # Allow some extra time
        for dm in daa:
            dm.checkRR()
    t3 = ticks_us()
    #=================Print out analysis results=================
    smx.active(0)               # Turn off the state machine
    for dm in daa:   dm.dms.active(0) # Turn off the DMAs
    print(f'Turned off SM and DMAs at t+{t3-t0} us, vs {nomTTime} nominal')
    sleep_us(10000)
    for dm in daa:  dm.checkRR()
    print()
    #for dm in daa:  dm.checkBuffer() #checkBuffer(dm.wa)
    #=======================/End of main\========================
if __name__ == "__main__":
    wa = main()
