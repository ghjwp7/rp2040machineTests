.. -*- mode: rst -*-  #  RM for dmaCtrlRegBits.py - jiw - 1 Jan 2025
..  To view this in html in browser, use `restview fn` (fn=this file)
..  Browser page updates when changed version is stored.

========================================
dmaCtrlRegBits.py & testDCRB.py
========================================

DMA control registers like `CHx_CTRL_TRIG, CHx_AL1_CTRL,
CHx_AL2_CTRL,` and `CHx_AL3_CTRL` on an RP2040 system (eg, a Raspberry
Pi Pico or Zero) are 32-bit registers that contain 16 fields
controlling how a DMA channel behaves.  Table 124 in the RP2040
Datasheet shows field names and widths.  One could manually decode
control register values, but using a program as described here can
save time and effort when decoding such values.

`dmaCtrlRegBits.py` contains four small functions to assist in
decoding or printing values of bit fields from a packed DMA control
register value.  `testDCRB.py` imports functions from
`dmaCtrlRegBits.py` and runs tests.

--------------------------------------
Example Output from testDCRB.py
--------------------------------------

Output shown below is from `testDCRB`.  The first section shows the
tuple that `dmaCtrlRegBits.fieldList()` returns.  [Line-breaks added
for readability.] For each field, the tuple has a tuple with field name
and number of bits in field.  Example: `treq_sel` field is 6 bits
long.  Note, see Table 124 in Datasheet for field explanations. ::

    fieldList(): (('enable', 1), ('high_pri', 1), ('size', 2),
    ('inc_read', 1), ('inc_write', 1), ('ring_size', 4), ('ring_sel', 1),
    ('chain_to', 4), ('treq_sel', 6), ('irq_quiet', 1), ('bswap', 1),
    ('sniff_en', 1), ('busy', 1), ('reserved', 4), ('write_err', 1),
    ('read_err', 1), ('ahb_err', 1))

The second section of `testDCRB` output shows byte arrays returned by
five calls to `dmaCtrlRegBits.unpackVals(p)`, for hex values of `p` as
in parentheses. ::

                                           sz ir iw         treq         bz    we re ae
    unpackVals(01200025): array('b', [1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0])
    unpackVals(01200029): array('b', [1, 0, 2, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0])
    unpackVals(00220021): array('b', [1, 0, 0, 0, 1, 0, 0, 0, 4, 1, 0, 0, 0, 0, 0, 0, 0])
    unpackVals(003f8021): array('b', [1, 0, 0, 0, 1, 0, 0, 0, 63, 1, 0, 0, 0, 0, 0, 0, 0])
    unpackVals(003f8025): array('b', [1, 0, 1, 0, 1, 0, 0, 0, 63, 1, 0, 0, 0, 0, 0, 0, 0])

The last section of `testDCRB` output shows a title printed by
`dmaCtrlRegBits.printHeadLines()`, followed by output from five calls
to `dmaCtrlRegBits.printCodes(p)`. ::

              enab high size inc_ inc_ ring ring chai treq irq_ bswa snif busy rese writ read ahb_
                le _pri      read writ _siz _sel n_to _sel quie    p f_en      rved e_er _err  err
    01200025    1    0    1    0    1    0    0    0    0    1    0    0    1    0    0    0    0
    01200029    1    0    2    0    1    0    0    0    0    1    0    0    1    0    0    0    0
    00220021    1    0    0    0    1    0    0    0    4    1    0    0    0    0    0    0    0
    003f8021    1    0    0    0    1    0    0    0   3f    1    0    0    0    0    0    0    0
    003f8025    1    0    1    0    1    0    0    0   3f    1    0    0    0    0    0    0    0

--------------------------------------
  Test Environment
--------------------------------------

Code was tested 5 Jan 2025 in Python 3.10.12 on an ubuntu.22.04 Linux
system.  When running this test on an RP2040-based system with
MicroPython, both of `testDCRB.py` and `dmaCtrlRegBits.py` need to be
on the system.

jiw - 5 Jan 2025

