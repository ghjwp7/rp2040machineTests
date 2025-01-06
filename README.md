.. -*- mode: rst -*- # README for some small test progs
.. - jiw - 4 Jan 2025
..  To view this as html in browser, use `restview README.rst &`
..  Browser page will update whenever a changed version is stored.

========================================
PIO, DMA, Timer tests / demos
========================================

This repo contains several small test or demonstration programs, for
PIO, DMA, Timer devices on an RP2040-based system, as typified by a
Raspberry Pi Pico.

------------------

🔵 See [README-lPIODMAt.rst](README-lPIODMAt.rst)
[README-lPIODMAt](README-lPIODMAt.md)
[README-lPIODMAt](./README-lPIODMAt.md)  for description of
`littlePIO-DMAtest1`, a demonstration of putting RP2040 PIO State
Machine output into memory, via DMA transfer.  That `README` describes
a PIO-DMA test program and shows example output.

------------------

🔵 See `README-readTimerReg.rst` for description of `readTimerReg.py`,
a demonstration of directly reading an RP2040's main timer register
several ways.  That `README` describes the test program and shows
example output.  The program tests at multiple system frequencies.

------------------

🔵 See `README-sDMAregs.rst` for description of `showDMAregisters.py`,
a demonstration of looking at RP2040 DMA register contents via a
`memoryview` object supplied by `DMA.registers`.  That `README`
describes the test program and shows example output for three DMA
channels it sets up.

------------------

🔵 See `README-dmaCRB.rst` for description of `dmaCtrlRegBits.py` and
`testDCRB.py`, a demonstration of decoding RP2040 DMA control register
contents.  That `README` lists helper routines that can be imported
from `dmaCtrlRegBits.py` and shows output from test program
`testDCRB.py`.

------------------

Note, code tests mentioned in these READMEs ran on an RP2040
board with MicroPython v1.25.0, via Thonny 3.3.14 IDE on an
ubuntu.22.04 Linux system.  The board is labeled 'RP2040-Zero' but
detects as 'Raspberry Pi Pico with RP2040'::

    MicroPython v1.25.0-preview.160.gc73204128 on 2024-12-30; Raspberry Pi Pico with RP2040
    Type "help()" for more information.
    >>> 

jiw - 5 Jan 2025