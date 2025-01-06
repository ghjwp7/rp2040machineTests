#!/bin/env python
# -*- mode: python;  coding: utf-8 -*-  jiw - 5 Jan 2025
#  RP2040 DMA testing: demo that dmaCtrlRegBits.py functions work ok atm
import dmaCtrlRegBits as cb

def main():
    # test that  fieldList()  returns tuple of (name, nbits) pairs
    print('fieldList():', cb.fieldList())
    # test print of  unpackVals(p)  in a form like:
    #      unpackVals(00220021): array('b', [1, 0, 0, 0, 1, 0, 0, 0, 4, 1, 0, 0, 0, 0, 0, 0, 0])
    print('                                       sz ir iw         treq         bz    we re ae')
    for p in (0x1200025, 0x1200029, 0x220021, 0x3f8021, 0x3f8025):
        print(f'unpackVals({p:08x}): {cb.unpackVals(p)}')
    print()
    # test:  printHeadLines(), printCodes(p)
    cb.printHeadLines()
    for p in (0x1200025, 0x1200029, 0x220021, 0x3f8021, 0x3f8025):
        cb.printCodes(p)
if __name__ == "__main__":
    main()
