# -*- mode: python;  coding: utf-8 -*-  jiw - 13 Jan 2025

# memoryAlign 4 -- Routine to allocate memory at specified alignment,
# eg 128, 256, 512, 1024 ... for DMA circular buffers.
# Ref: Initialising byte array at specific memory boundary
# https://github.com/orgs/micropython/discussions/12095

# In this version we try allocating and releasing successively larger
# arrays, until we get to one that contains a good alignment, which we
# return part of.  The allocated length does not exceed 2*align+needed

from gc      import collect
from uctypes import addressof, bytearray_at
from array   import array

def aligner(align, nBloks): # Block size = align
    collect()
    btot = align*(nBloks+1)
    ba  = bytearray(btot)
    bad = addressof(ba)
    
    aa = bytearray_at(bad+align-(bad%align), btot-align)
    aad = addressof(aa)
    adab = aad - bad
    #print(f' {align=:x} {nBloks=} {btot=:x} {bad=:x} {bad%align=:x}  {adab=:x}')
    return aa

def main():
    for a, n in ((128, 4), (256, 1), (1024, 3)):
        ba = aligner(a, n)
        baa = addressof(ba) if ba else 0
        print(f'{a=:5x}   {n=}   {baa=:8x}   {baa%a=:x}')

if __name__ == "__main__":
    print('Calling main')
    main()
