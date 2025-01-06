# -*- mode: python;  coding: utf-8 -*-  jiw - 3 Jan 2025
#  RP2040 DMA test: allocate some DMA channels and print register contents
from array   import array
from rp2     import DMA
from uctypes import addressof
def main():
    DREQ_PIO0_TX0 = 0    # From 2.5.3.1. DREQ Table in Datasheet
    DREQ_PIO0_RX0 = 4    # From 2.5.3.1.
    TREQ_PERMANENT=0x3f  # From 2.5.7, table 124, p. 112, bit field 20:15
    slen = 33; step = 0x01010101;  base = 5
    sa = array('I', range(step*base, step*(base+slen), step)) # Gen slen*4 bytes
    print(f'addressof(sa): {addressof(sa):22x}{addressof(sa):11x}{addressof(sa):11x}')
    print(f'addressof(da):            ', end='')
    daa = [0,0,0]
    dmx, dmy, dmz = DMA(), DMA(), DMA() # Make DMA data structures
    dms = ((0,dmx,'x'), (1,dmy,'y'), (2,dmz,'z'))
    for j, d, l in dms:
        dc = dmx.pack_ctrl(size=j,  # Select 2^j-byte xfers
                           inc_write=True, inc_read=False,
                           #trigger=False,
                           #treq_sel=TREQ_PERMANENT)
                           #treq_sel=DREQ_PIO0_TX0)
                           treq_sel=DREQ_PIO0_RX0)
        tcode = ('B', 'H', 'I')[j] # Get type code for 1, 2, 4 bytes
        daa[j] = da = array(tcode, [0]*slen)
        print(f'{addressof(da):11x}', end='')
        # Put DMA data structure into registers.  Ref table 124 on
        # p. 113 of Datasheet for layout of CHx_CTRL_TRIG.  Field 3:2
        # is DATA_SIZE, so goes up by 4 from x to y and y to z
        d.config(read=sa, write=da, count=slen, ctrl=dc, trigger=False)
    print()
    #for j in range(3): print(daa[j][:5])
    p, q, r = dmx.registers, dmy.registers, dmz.registers
    rnames = (
        'CHx_READ_ADDR', 'CHx_WRITE_ADDR', 'CHx_TRANS_COUNT', 'CHx_CTRL_TRIG',
        'CHx_AL1_CTRL', 'CHx_AL1_READ_ADDR', 'CHx_AL1_WRITE_ADDR',
        'CHx_AL1_TRANS_COUNT_TRIG', 'CHx_AL2_CTRL', 'CHx_AL2_TRANS_COUNT',
        'CHx_AL2_READ_ADDR', 'CHx_AL2_WRITE_ADDR_TRIG', 'CHx_AL3_CTRL', 
        'CHx_AL3_WRITE_ADDR', 'CHx_AL3_TRANS_COUNT', 'CHx_AL3_READ_ADDR_TRIG',
        'filler')
    # Each channel has 16 regs in control block, as listed above; so
    # we end with exception "IndexError: memoryview index out of range"
    try:
        for j in range(17):
            if 0==j:
                print('{:32} dm{:8} dm{:8} dm{:8}'.format('', 'x', 'y', 'z'))
            elif 0==j%4: print() 
            print(f'{j*4:02x} {rnames[j]:24}  {p[j]:8x}   {q[j]:8x}   {r[j]:8x}')
    except:
        print('Exceptional!')
    print(' dmx,y,z registers are at ', end='')
    for j, d, l in dms:
        print(f'{addressof(d.registers):11x}', end='')
    print()
    #for j in range(3): print(daa[j][:11])
    #for d in (dmx, dmy, dmz): d.active(1)
    #for j in range(3): print(daa[j][:11])
if __name__ == "__main__":
    main()

