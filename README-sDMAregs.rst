.. -*- mode: rst -*-  #  RM for showDMAregisters.py - jiw - 1 Jan 2025
..  To view this in html in browser, use `restview README-sDMAregs.rst`
..  Browser page updates when changed version is stored.

========================================
showDMAregisters
========================================

**Aim:** On an RP2040, `showDMAregisters` demonstrates allocation and
setup of some DMA channels, and looking at RP2040 DMA register
contents via a `memoryview` object, as supplied by `DMA.registers`.
`showDMAregisters` prints a labeled table of register contents.

In general, `memoryview` areas may be readable/writable.  Some
micropython `memoryview`'s related to IO are readonly but the control
area referenced by `DMA.registers` appear to be read/write, as shown
by this example, run within thonny's shell window::

    >>> from rp2 import DMA
    >>> g=DMA(); r=g.registers; print(r[0]); r[0]+=4; print(r[0])
    536891648
    536891652

**What program does:** At the outset, `showDMAregisters` sets up a
source array.  It then says ::

    dmx, dmy, dmz = DMA(), DMA(), DMA()

to create three DMA-channel data structures, then in a loop creates
three destination arrays, operates on `dmx, dmy, dmz` to set DMA
parameters, and configures three DMA channels by copying `dmx, dmy,
dmz` data structures into registers in the DMA-hardware memory map.
Heading lines like ::

    addressof(sa):       20005100   20005100   20005100
    addressof(da):       20005480   200056b0   20005900  

are printed so that those hexadecimal addresses can be recognized in
the register printout the program shows next::

                             dmx        dmy        dmz       
    00 CHx_READ_ADDR     20005100   20005100   20005100
    04 CHx_WRITE_ADDR    20005480   200056b0   20005900
    08 CHx_TRANS_COUNT         21         21         21
    0c CHx_CTRL_TRIG      1200021    1200025    1200029

The next dozen lines of output (see example-output section) show
contents of three sets of DMA alias registers, followed by these lines::

    Exceptional!
     dmx,y,z registers are at 50000000 50000040 50000080

Those hexadecimal addresses are base addresses for register sets of
DMA channels 0, 1, and 2.  See Table 120, 'List of DMA registers',
pp. 101-110 in section 2.5.7 of the RP2040 Datasheet, or see Tables
121-152 on pp. 111-121 of the same section.

'Exceptional!' appears as a consequence of ::

    except:
        print('Exceptional!')

which executes because of a ::

    "IndexError: memoryview index out of range"

exception occurring when the register printing loop runs off the end
of the 16-word `memoryview` object that `DMA.registers` provided.

--------------------------------------
 Example Output
--------------------------------------

Note, transfer counts are numbers of transfers.  0x21 = 33 decimal.
In this example output -- for which treq_sel = DREQ_PIO0_TX0, and that
PIO was inactive, so the DMA did not run -- the `dmx` setup will
transfer 33 bytes; `dmy`, 33 half-words or 66 bytes; and `dmz`, 33
words or 132 bytes. ::

    addressof(sa):               20005100   20005100   20005100
    addressof(da):               20005480   200056b0   20005900
                                     dmx        dmy        dmz       
    00 CHx_READ_ADDR             20005100   20005100   20005100
    04 CHx_WRITE_ADDR            20005480   200056b0   20005900
    08 CHx_TRANS_COUNT                 21         21         21
    0c CHx_CTRL_TRIG              1200021    1200025    1200029
    
    10 CHx_AL1_CTRL               1200021    1200025    1200029
    14 CHx_AL1_READ_ADDR         20005100   20005100   20005100
    18 CHx_AL1_WRITE_ADDR        20005480   200056b0   20005900
    1c CHx_AL1_TRANS_COUNT_TRIG        21         21         21
    
    20 CHx_AL2_CTRL               1200021    1200025    1200029
    24 CHx_AL2_TRANS_COUNT             21         21         21
    28 CHx_AL2_READ_ADDR         20005100   20005100   20005100
    2c CHx_AL2_WRITE_ADDR_TRIG   20005480   200056b0   20005900
    
    30 CHx_AL3_CTRL               1200021    1200025    1200029
    34 CHx_AL3_WRITE_ADDR        20005480   200056b0   20005900
    38 CHx_AL3_TRANS_COUNT             21         21         21
    3c CHx_AL3_READ_ADDR_TRIG    20005100   20005100   20005100
    
    Exceptional!
     dmx,y,z registers are at    50000000   50000040   50000080

Note, CHx_AL are generally the same registers as the first four, but
in different orders and trigger settings, intended for use in
chaining, scatter, gather, etc. as explained in Datasheet section
2.5.2.1, 'Aliases and Triggers'.

--------------------------------------
  CHx_CTRL_TRIG encoding
--------------------------------------


Table 124 (pp. 113-114 in Datasheet) breaks out 16 fields encoded in
the DMA control register class, which comprises registers
`CHx_CTRL_TRIG` and its aliases, `CHx_AL1_CTRL, CHx_AL2_CTRL,
CHx_AL3_CTRL`.  The control values shown for the three DMA channels
shown in the example differ in the `DATA_SIZE` field, bits 3:2, with
values 00, 01, and 10 representing byte, half-word, and word transfer
sizes.   Bits 14:11, the `CHAIN_TO` field, is 0 in all three values,
[although Table 124 implies that field should contain the channel
number, 0, 1, 2 in the x,y,z cases, if chaining is not intended].

Bits 20:15 are the `TREQ_SEL` field; when one changes `TREQ_SEL` among
DREQ_PIO0_TX0, DREQ_PIO0_RX0, and TREQ_PERMANENT, control word values
like 1200021, 1200025, 1200029, 220021, 220025, 220029, 3f8021,
3f8025, and 3f8029 appear.  Some of these decode as follows (as
displayed by program `dmaCtrlRegBits.py`; see `README-dmaCRB.rst`)::

              enab high size inc_ inc_ ring ring chai treq irq_ bswa snif busy rese writ read ahb_
                le _pri      read writ _siz _sel n_to _sel quie    p f_en      rved e_er _err  err
    01200025    1    0    1    0    1    0    0    0    0    1    0    0    1    0    0    0    0
    01200029    1    0    2    0    1    0    0    0    0    1    0    0    1    0    0    0    0
    00220021    1    0    0    0    1    0    0    0    4    1    0    0    0    0    0    0    0
    003f8021    1    0    0    0    1    0    0    0   3f    1    0    0    0    0    0    0    0
    003f8025    1    0    1    0    1    0    0    0   3f    1    0    0    0    0    0    0    0




--------------------------------------
  Future
--------------------------------------

Count registers typically showed up as 0 in these tests, probably
indicating transfer had completed before the test code read out the
registers, or that setup wasn't properly done.  Future: add
`dmx.active(0)` etc at one or two places and see effect.

--------------------------------------
  Test Environment
--------------------------------------

Code was tested ca 4 Jan 2025 using a small inexpensive board labeled
RP2040-Zero running MicroPython v1.25.0-preview.160, via Thonny 3.3.14
IDE on an ubuntu.22.04 Linux system.  ::

    MicroPython v1.25.0-preview.160.gc73204128 on 2024-12-30; Raspberry Pi Pico with RP2040
    Type "help()" for more information.
    >>> 

jiw - 4 Jan 2025

