# -*- mode: python;  coding: utf-8 -*-  jiw - 5 Jan 2025
# Four routines for decoding/printing RP2040 DMA Control Register bits
from array import array

def fieldList(): # Return tuple of (name,bits) tuples, one per control-reg field (+reserved)
    #  Adapted by text editing from rp2_dma_ctrl_fields_table[] at line 59 of rp2_dma.c 
    #  in micropython distribution source directory micropython/ports/rp2
    return (("enable", 1),
         ("high_pri",  1),  ("size",      2),  ("inc_read",  1),  ("inc_write", 1),
         ("ring_size", 4),  ("ring_sel",  1),  ("chain_to",  4),  ("treq_sel",  6),
         ("irq_quiet", 1),  ("bswap",     1),  ("sniff_en",  1),  ("busy",      1),
         ("reserved",  4),  ("write_err", 1),  ("read_err",  1),  ("ahb_err",   1))

def unpackVals(p):  # Given a packed control-reg value, return field values byte array
    f = fieldList();   n = len(f)
    v = array('b', [0]*n)
    for j in range(n):
        t, b = f[j]
        v[j] = p & ((1<<b)-1)   # Make mask with b bits
        p >>= b                 # Shift out used bits
    return v

def printHeadLines(): # Print titles from fieldList, split across 2 lines
    for c in (0,4):
        print('         ', end='')
        for t,b in fieldList():
            print(f'{t[c:c+4]:>5}', end='')
        print()

def printCodes(p): # Unpack & print fields of control-reg value p, in 5-wide hex
    print(f'{p:08x}', end='')
    for v in unpackVals(p):
        print(f'{v:5x}', end='')
    print()
