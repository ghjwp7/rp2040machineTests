# -*- mode: python;  coding: utf-8 -*-  jiw - 23 Dec 2024, 20 Jan 2025

#  calibratePulse8b -- This tests / demos an edge-timing method like
#  that of calibratePulse1, except that de-noise code is removed,
#  removing need in app program to correct for deadtime.  See notes in
#  README-calP1.rst.  8a versions didn't use DMA to store data. 8b
#  will, via code from PIO-DMAtest2 in rp2040machineTests github repo.

#  Hardware requirement for 8b testing: Jumper from output pin 13 to
#  input pin 12.  Unlike 8a, 8b doesn't use SSD1306 display.

#  Besides ordinary square waves for testing, this code can produce
#  waves with 3% or 97% duty cycles, which were intended as
#  noise-simulation sequences, like with a spike at the front or the
#  end.  An earlier version of pulseTiming code has some noise
#  detection code, discarded in this version to simplify getting a
#  working program.  To select different duty cycles, set waveType to
#  1, 2, or 3.  A later version could cycle thru all wave types, in
#  phases that also change wave frequency.  Not a priority item.

from makeCounters import makeCounter
from machine import freq, Pin
from rp2     import PIO, asm_pio, StateMachine
from utime   import sleep_us, ticks_us
# =const(7457)  # from machine import freq; freq(000000); freq()
#-----------------------------------------------------------
W_out_Pin=const(13)    # Wave SM output pin
C_in_Pin=const(12)     # Counter input pin
NEdges=const(8000)    # Number of wave edges we'll observe
#WaveFreq=const(331)  # Desired wave rate from wave state machine
SysFreq=const(120000000) # Desired RP2040 system frequency
# We need CycTot = 3+CycOut = 2+CycUp+CycDn
CycTot=const(20)       # usually 32, but can set as desired
CycUp=const(CycTot//2-1) # CycUp, CycDn are for ~ square wave
CycDn=const((CycTot+1)//2-1)
CycOut=const(CycTot-3) # CycOut is for low-duty or high-duty
#WaveSMFreq=const(WaveFreq*CycTot) # Step-frequency of wave SM
GRise=const(1)         # Data item = rising-edge time
GFall=const(0)         # Data item = falling-edge time
GStart=const(2)        # Data item = unused item
#-----------------------------------------------------------
#-----------makeSMwave starts a State machine---------------
#-----------to generate one of 3 pulse trains---------------
#-----------------------------------------------------------
def makeSMwave(snum, WaveSMFreq):   # Set up selected state machine snum
    @rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
    def pioProg1():             # Make a square wave
        set(pins, 1) [CycUp]    #    up
        set(pins, 0) [CycDn]    #    down
    @rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
    def pioProg2():             # Make a falling-spikes wave
        set(pins, 1)            # (CycTot-1) ~ up
        nop() [CycOut]          # Delay is added to usual 1~
        set(pins, 0)            # 1 ~ down
    @rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
    def pioProg3():             # Make a rising-spikes wave
        set(pins, 1)            # 1 ~ up
        set(pins, 0)            # (CycTot-1)~ down
        nop() [CycOut-1]

    if 1 <= snum <= 3:
        # Duty cycle = highCycles/CycTot
        highCycles = (CycUp+1, CycTot-1, 1)[snum-1]
        pio = (pioProg1, pioProg2, pioProg3)[snum-1]
        #print(f'{snum=}  {highCycles=}  ')
        pino = Pin(W_out_Pin, Pin.OUT)
        sm = StateMachine(snum, pio, freq=WaveSMFreq, set_base=pino)
        return sm, highCycles
    else:
        print('Invalid snum {snum}');  sys.exit()
#--------------------------------------------------------
#@micropython.native
def takeReadings(wsm, cycHi, waveRatio, counterFreq, splitF):
    cycDown   = CycTot-cycHi
    # waveRatio = counter counts per wave cycle
    nomCycles = round(waveRatio*CycTot)
    nomUpCy = round(cycHi*waveRatio/CycTot)   # ~ Up cycles
    nomDnCy = round(cycDown*waveRatio/CycTot) # ~ Down cycles

    hsize = 13            # Number of histogram bins to maintain
    m = hsize//2;  e = hsize-1
    def bounds(nomcy):    # Make set of bin limits, centered at nomcy
        ba = [nomcy]*hsize; 
        for j, d in enumerate((1, 2, 5, 10, 20, 50)):
            ba[m+1+j] = nomcy+d
            ba[m-1-j] = nomcy-d # Center the set of bins at nominal count
        #print(f'{nomcy=}  {ba=}')
        return ba          # Return the list of bin limits

    #d=value, b=bin limits, h=bins.  Increment the bin that d belongs to. 
    def hentry(d, b, h):
        if   d== b[m]:     h[m] += 1
        elif d < b[m]:
            if d== b[m-1]: h[m-1] += 1 # nomcy+1
            elif d<= b[0]:   h[0] += 1 # " 50
            elif d<= b[1]:   h[1] += 1 # " 20
            elif d<= b[2]:   h[2] += 1 # " 10
            elif d<= b[3]:   h[3] += 1 # " 5
            elif d<= b[4]:   h[4] += 1 # " 2
        else:
            if d== b[m+1]:   h[m+1] += 1 # nomcy-1
            elif d>= b[e-0]: h[e-0] += 1 # " 50
            elif d>= b[e-1]: h[e-1] += 1 # " 20
            elif d>= b[e-2]: h[e-2] += 1 # " 10
            elif d>= b[e-3]: h[e-3] += 1 # " 5
            elif d>= b[e-4]: h[e-4] += 1 # " 2

    histGR, histGF = [0]*hsize, [0]*hsize
    baseGR = bounds(nomDnCy)
    baseGF = bounds(nomUpCy)
    # This section creates & activates csm and takes a set of readings
    pini = Pin(C_in_Pin, Pin.IN)  # Counter input pin
    # Init. csm on PIO 1, with wsm on PIO 0, to allow more steps
    csmPIO = makeCounter(splitF)
    csm = StateMachine(7, csmPIO, freq=counterFreq, jmp_pin=pini)
    sleep_us(50000) # Let system settle
    wsm.active(1)   # Start wave-making state machine
    ## Wait for high level of wave before starting counter.  We don't
    ## have enough PIO SM instruction words to check this in csm.
    #while pini.value()==0: pass
    csm.active(1)   # Start the counter; it will sync on first falling edge
    KBuf=const(8)
    totGR = totGF = 0
    i = 0;   xprev = 0; skips = 0; ks = 0;  ka = [0]*2*KBuf
    t0 = ticks_us()
    while i < NEdges:
        mark = csm.get()
        while mark >= GStart:
            mark = csm.get()    # Sync with a GR or GF
            skips += 1
        i += 1
        xlast = csm.get()
        d = xlast - xprev;   xprev = xlast
        ka[ks], ka[ks+1] = mark, xlast # Keep some entries from ends
        ks = ks+2 if ks+2 < 2*KBuf else KBuf
        # Make histogram entry
        if   mark==GRise:
            hentry(d, baseGR, histGR);  totGR += d
        elif mark==GFall:
            hentry(d, baseGF, histGF);  totGF += d
    t1 = ticks_us()
    wsm.active(0)     # Stop wave-making SM
    csm.active(0)     # Stop counter SM
    
    # Clear all programs in both PIOs, to avoid later [Errno 12] ENOMEM OSError
    for j in (0,1):
        p = PIO(j)
        PIO.remove_program(p)

    return (histGR,histGF), (baseGR,baseGF), (totGR,totGF), xlast, skips, t0, t1, ka
#--------------------------------------------------------
def shoHisto(hist, base, waveRatio):
    print(f'{'Histogram Results':^60}')
    hsize = len(hist[0]);  m = hsize//2;  e = hsize-1
    trav = rnom = 0
    for j in (0,1):
        label = ('GR','GF')[j]
        hj, bj = hist[j], base[j]
        if sum(hj) == 0: continue # Skip over if no counts in bin
        rsum = max(1, sum(hj[k] for k in range(1,e)))
        rav = sum(hj[k]*bj[k] for k in range(1,e))/rsum
        trav += rav;  rnom += bj[m] # wha rnom?
        ncase = sum(hj)
        print(f'{ncase:6} {label}: {bj[m]:6} nom, {rav:10.4f} avle    ', end='')
        for k in range(hsize):
            h, b = hj[k], bj[k]
            if h>0:
                if   k==0:  print(f'≤{b}: {h}  ', end='')
                elif k==e:  print(f'≥{b}: {h}', end='')
                elif m-2 < k < m+2:  print(f'={b}: {h}  ', end='')
                elif k < m: print(f'({bj[k-1]}-{b}]: {h}  ', end='')
                else:       print(f'[{b}-{bj[k+1]}): {h}  ', end='')
        print()
        #print(f'{rav=:10.4f}  {trav=:10.4f}  {rnom=}')
    print(f'Total average (less edges) = {trav:10.5f}, nomCy {waveRatio:7.5f}, total nom {rnom}')
#--------------------------------------------------------
# showFRSplit -- Make output to go into table of following form.
# ========= =========  ========  ======  ======  =======  =======
#   Edges   WaveFreq   FR Split   R Bin   F Bin  R Count  F Count
# ========= =========  ========  ======  ======  =======  =======
#   702        6003     4-7  *    4998     4999    4997     4999
# ========= =========  ========  ======  ======  =======  =======

def showFRSplit(h, b, tGs, WaveFreq, DXF, DXR, krn, kfn):
    # Get main entries from rising and falling histos and bases
    #for h, b in zip(histos, bases): print(f'{h=}\n{b=} ')
    def getMainCell(j):
        m = max(h[j])
        return m, b[j][h[j].index(m)]
    #print('========= =========  ========  ======  ======  =======  =======')
    #print('  Edges   WaveFreq   FR Split   R Bin   F Bin  R Count  F Count')
    rc, rb = getMainCell(0)
    fc, fb = getMainCell(1)
    v = len(b[0])//2; nomcy = b[0][v]+b[1][v]
    totGR, totGF = tGs; tdelta = totGR-totGF;  kdelta = krn-kfn
    smark = '*' if rc==fc and rb==fb else ' '
    kerr = nomcy-2*tdelta
    kmark = '*' if kerr<3 else '+' if kerr<31 else ' '
    #print(f'  {NEdges} {WaveFreq}  {DXF:}-{DXR}{smark} {krn=} {kfn=} knΔ={kdelta:6} {nomcy=:6}  totΔ={tdelta:<6}{kmark}  {totGR=}  {totGF=}')
    #print(f'  {NEdges} {WaveFreq}  {DXF:}-{DXR}{smark} {krn=} {kfn=} knΔ={kdelta:6} {nomcy=:6}  {totGR=} {totGF=}  {kerr=:<6}')
    print(f'   {WaveFreq}  {DXF:}-{DXR}  {kerr=:>6}  {nomcy=:6} {totGR=} {totGF=} NE={NEdges} {krn=}')
    #print(f'{NEdges:7} {WaveFreq:7} {DXF:>8}-{DXR}{mark} {rb:9}{fb:8}{rc:9}{fc:9}')
#--------------------------------------------------------
def run1test(WaveFreq, splitF, ioOpt):
    if ioOpt & 32:
        print("Making state machine instances")
    waveType = 1           # 1 = 50% up, 2 = 97% up, 3 = 3% up
    countSMFreq=freq();
    WaveSMFreq = WaveFreq*CycTot
    nsPerCount = 2e9/countSMFreq # 2 SM cycles per count
    nsPerWave  = 1e9/WaveFreq
    waveSeconds = (NEdges/2.0)/WaveFreq
    if ioOpt & 1:
        print(f'System frequency  = {freq():9} Hz, {1e9/freq():9.2f} ns')
        print(f'Counts per second = {countSMFreq//2:9} Hz, {nsPerCount:9.2f} ns')
        print(f'  Wave frequency  = {WaveFreq:9} Hz, {nsPerWave:9.2f} ns  from SM freq {WaveSMFreq}')
    if ioOpt & 32:
        print(f'About to get {NEdges} edges in {waveSeconds:3.1f} sec. with wave type {waveType}')
    waveRatio = (countSMFreq/WaveFreq)/2   # counter counts per wave-cycle
    # Make wave state machine
    sm, cycUp = makeSMwave(waveType, WaveSMFreq)
    # Make counter, get data
    r = takeReadings(sm,cycUp,waveRatio,countSMFreq, splitF)

    histos, bases, totGs, xlast, skips, t0, t1, ka = r
    nitems = sum(sum(h) for h in histos)
    td = t1-t0;  tlast = nsPerCount*xlast/1000
    terr = 1000*(td-tlast)/nitems
    pt_tl = 1e6*waveSeconds - tlast
    if ioOpt & 2:
        print(f'Processed {nitems} items with {skips} skips in {td/1e6:8.6f} sec\n')
        # Use x.1f in several items below to avoid fake accuracy w/ 6-7 FP digits.
        print(f'Clock time {td:12} us   Clock-count total diff{td-tlast:7.1f} us')
        print(f'Counted time {tlast:12.1f} us   Clock-count avg diff {terr:8.3f} ns')
        print(f'Predicted time {1e6*waveSeconds:10.1f} us      less counted time{pt_tl:7.1f} us\n')

    if ioOpt & 4:
        shoHisto(histos, bases, waveRatio)
    krb=[ka[j+1] for j in range(0,KBuf,2) if ka[j]==GRise]
    kre=[ka[j+1] for j in range(KBuf,2*KBuf,2) if ka[j]==GRise]
    kfb=[ka[j+1] for j in range(0,KBuf,2) if ka[j]==GFall]
    kfe=[ka[j+1] for j in range(KBuf,2*KBuf,2) if ka[j]==GFall]
    krn = kre[-1]-krb[0];  kfn = kfe[-1]-kfb[1] # don't like kfb[0]
    if ioOpt & 16:
        print(f'{krn=}   krn/NE: {krn/NEdges:4.6f}   krn/nomCy: {krn/waveRatio:4.6f}   krn%|nomCy|: {krn%int(waveRatio)}')
        print(f'{kfn=}   kfn/NE: {kfn/NEdges:4.6f}   kfn/nomCy: {kfn/waveRatio:4.6f}   kfn%|nomCy|: {kfn%int(waveRatio)}')

    if ioOpt & 8:
        DXF, DXR = splitF, 11-splitF
        showFRSplit(histos, bases, totGs, WaveFreq, DXF, DXR, krn, kfn)

    if ioOpt & 32:
        print(f'{CycTot=} {CycUp+CycDn=} {CycUp=} {CycDn=}  {CycOut=}  {WaveSMFreq=}')
        print(f'{waveSeconds=}  {NEdges=}  {WaveFreq=}  {NEdges/WaveFreq=}\n{NEdges/WaveFreq/2=}   {freq()=}   {waveRatio=}')
        print(f'{ka=}')
        print(f'{krb=} {kre=}  {kfb=}  {kfe=}')
#==========================================================
def main():
    freq(SysFreq); freq(SysFreq) # Set system frequency as desired
    # showFRSplit
    #print('  Edges   WaveFreq   FR Split   R Bin   F Bin  R Count  F Count')
    for wf in (440,500,600,700):
        for spf in (3,4,5,6,7,8):
            run1test(wf, spf, 8)
#==========================================================
if __name__ == "__main__":
    main()