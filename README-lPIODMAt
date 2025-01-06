.. -*- mode: rst -*-  #  RM for littlePIO-DMAtest1.py - jiw - 1 Jan 2025
..  To view this in html in browser, use `restview README-lPDt.rst`
..  Browser page will update whenever a changed version is stored.

========================================
littlePIO-DMAtest1
========================================

**Aim:** `littlePIO-DMAtest1` is a test or demo of putting RP2040 PIO
State Machine output into memory, via DMA transfer.  It acts as follows:

• Creates a state machine `smx` to increment a counter by 3 between stores
• Sets up a DMA channel that will transfer 200 words from `smx` to an array
• Runs a wait loop reporting on progress of filling the array
• At end, runs report loops to drain remaining items out of `smx`'s Rx fifo
  (which includes new elements arriving before the report finishes)

Note, `smx` has its two 4-word Rx and Tx fifos combined into one 8-word Rx
fifo, by dint of `fifo_join=PIO.JOIN_RX` in the `@rp2.asm_pio()` parameter list.

**Example Output:** ::

    System frequency   = 125000000
    SM  step frequency =      2000
    SM cycle frequency =    333.33 Hz = 3000 us
    DMA count= 200 191 180 170 160 150 140 130 120 109 99 89 79 69 59 49 39 28 18 8
    At t=607934 us after 200 readings in 600000 us nominal time --
    first,last= 3  600      Delta 597
    min: 3    avg: 301.50    max: 600
    rx_fifo count: 3
     1.  @t+5047 us, fifo→ 603
     2.  @t+5732 us, fifo→ 606
     3.  @t+6371 us, fifo→ 609
     4.  @t+6975 us, fifo→ 612
    rx_fifo count: 8
     1.  @t+109243 us, fifo→ 615
     2.  @t+109865 us, fifo→ 618
     3.  @t+110467 us, fifo→ 621
     4.  @t+111082 us, fifo→ 624
     5.  @t+111674 us, fifo→ 627
     6.  @t+112294 us, fifo→ 630
     7.  @t+112897 us, fifo→ 633
     8.  @t+113492 us, fifo→ 636
     9.  @t+114096 us, fifo→ 717
    10.  @t+114687 us, fifo→ 720
    rx_fifo count: 0

In this output, fifo data values 603 and 606 arrived into the fifo
between the DMA count going to 0 (terminating the DMA transfer) and
`fifoTell()` being called.  Values 609 and 612 arrived while
`fifoTell()` was running, while previous items were printing.  The
program then slept for 101 milliseconds.  From time t+7 ms through
about t+31 ms, the next 8 values -- 615 to 636 -- arrived.  Because
`smx` doesn't block, it continued counting, without being able to
store the 26 results it produced during the 79 ms between t+31 ms
(when fifo filled) and t+110 ms (when fifo draining resumed).  This
produced a gap in readings, between data items 636 and 717.

Note, code was tested 1 Jan 2025 on an RP2040 running MicroPython v1.25.0, via
Thonny 3.3.14 IDE on an ubuntu.22.04 Linux system.  ::

    MicroPython v1.25.0-preview.160.gc73204128 on 2024-12-30; Raspberry Pi Pico with RP2040
    Type "help()" for more information.
    >>> 

