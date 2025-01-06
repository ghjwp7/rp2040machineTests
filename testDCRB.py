#!/bin/env python
# -*- mode: python;  coding: utf-8 -*-  jiw - 5 Jan 2025
#  RP2040 DMA testing: see if dmaCtrlRegBits.py works

import dmaCtrlRegBits as cb

def main():
    print('fieldList():', cb.fieldList())
    print('                                       sz ir iw         treq         bz    we re ae')
    # Eg:  unpackVals(00220021): array('b', [1, 0, 0, 0, 1, 0, 0, 0, 4, 1, 0, 0, 0, 0, 0, 0, 0])

    for p in (0x1200025, 0x1200029, 0x220021, 0x3f8021, 0x3f8025):
        print(f'unpackVals({p:08x}): {cb.unpackVals(p)}')
    print()
    cb.printHeadLines()
    for p in (0x1200025, 0x1200029, 0x220021, 0x3f8021, 0x3f8025):
        cb.printCodes(p)
if __name__ == "__main__":
    main()

# Heading format --
#'                                       sz ir iw         treq         bz    we re ae'
# unpackVals(00220021): array('b', [1, 0, 0, 0, 1, 0, 0, 0, 4, 1, 0, 0, 0, 0, 0, 0, 0])

