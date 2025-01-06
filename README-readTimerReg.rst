.. -*- mode: rst -*-  #  README for readTimerReg.py  - jiw - 4 Jan 2025
.. To view this as html in browser, use `restview fn &` with fn = name
.. of this file.  Browser page updates when changed file is stored.

========================================
readTimerReg.py
========================================

**Aim:**  On an RP2040, `readTimerReg.py` demonstrates directly
accessing the RP2040's main timer register.  (RP2040 = processor in
Raspberry Pi Pico and many other boards.)

Four times each for each of three modes, `readTimerReg` takes 9
successive timer readings, subtracting a `t0` value from each.  After
taking all its readings, `readTimerReg` prints them out (grouped by
reading mode) and prints reading-to-reading values as well.

The three modes tested are: 🔸calling `ticks_us()`, as imported from
`utime`; 🔸accessing the TIMELR register at 12+TIMER_BASE =
12+0x40054000 via `mem32[]`; and 🔸accessing it via a `ptr32()`
reference within a viper-translated function.

Unsurprisingly, viper-compiled code is by far the fastest.  On the
other hand, code using mem32[] is rather slow.

In the output shown below, four runs for each mode are grouped
together.  Modes are shown in the mentioned order, ie, using
`ticks_us()`, using `mem32[]`, and using `ptr32()`.  The lefthand 9
numbers on each line are timer readings minus a `t0` starting time.
The righthand 9 numbers on each line are difference between
consecutive values.

The output shown is from an unusual run (at default system frequency,
125 MHz) where the last three `ptr32()` runs all had the same results.
In most runs, there were small variations (a tick or two) in times for
the `ptr32()` mode.

Tests run at other clock rates than the 125 MHz default system
frequency are discussed below, after the next section.

--------------------------------------
      Example 1 Output
--------------------------------------

🔵 Lines l-o show results of using `ticks_us()` to record the current
time in microseconds.  Loop times averaged slightly over 12 μs per pass. ::

    l   28   81   96  111  123  134  145  157  170  l  28 53 15 15 12 11 11 12 13
    m   13   30   42   52   63   75   88  100  112  m  13 17 12 10 11 12 13 12 12
    n   14   29   42   56   69   81   93  104  115  n  14 15 13 14 13 12 12 11 11
    o   12   25   37   48   60   73   83   95  106  o  12 13 12 11 12 13 10 12 11

🔵 Lines p-s show results of using `mem32[]` references to the
`TIMELR` register, as explained in section 4.6.5. of the RP2040
Datasheet.  That section has a lengthy list of timer registers,
together with their offsets from `TIMER_BASE`, the base address for
memory-mapped timer registers.  Loop times averaged around 38 μs per
pass. ::

    p   52  142  186  226  263  301  336  374  411  p  52 90 44 40 37 38 35 38 37
    q   30   78  117  153  189  226  264  300  335  q  30 48 39 36 36 37 38 36 35
    r   29   78  120  157  194  231  268  306  344  r  29 49 42 37 37 37 37 38 38
    s   30   82  123  163  198  236  273  309  347  s  30 52 41 40 35 38 37 36 38

🔵 Lines u-x show results of using `ptr32()` [which is available
within viper-compiled code] to access `TIMELR`.  This method is able
to store timer readings at 4 μs intervals, with each reading offset
against a `t0` value. ::

    u    1   10   14   18   22   26   30   34   38  u   1  9  4  4  4  4  4  4  4
    v    0    5    9   13   17   21   25   29   33  v   0  5  4  4  4  4  4  4  4
    w    0    5    9   13   17   21   25   29   33  w   0  5  4  4  4  4  4  4  4
    x    0    5    9   13   17   21   25   29   33  x   0  5  4  4  4  4  4  4  4

-------------------

--------------------------------------
   Tests run at other clock rates
--------------------------------------

In its current version, `readTimerReg` will run sets of tests at
various system frequencies not below `underLimit` or above
`speedLimit`, as set at the beginning of `main`.  Let f0 be the system
frequency (typically 125 MHz) when the program starts.  `main` calls
`runTest(f)` for each in-limits frequency `f` from the list (f0,
100000000, 200000000, 250000000, f0).  Note, `runTest(f)` may try
twice to set a requested system frequency, because the program did not
succeed in changing from 250 MHz to 125 MHz with only one try.

Note, frequencies beyond 133 MHz are out-of-spec for the RP2040, and
the program as shown says `speedLimit = 133000001`.  However, in my
testing it worked ok at 200 MHz and 250 MHz, with the times for the
first and third access methods always decreasing proportionately to
system cycle time.

Times for `mem32[]` access, on the other hand, were sometimes
anomalous.  If `underLimit` and `speedLimit` both are 125000000, loop
times typically average around 38 μs per pass.  With `speedLimit` at
250000000, loop times typically average half that.  However, as seen
in the following results (from successive `runTest` passes) `mem32[]`
access times (lines p,q,r,s) on occasion sharply decreased, to less
than half their typical values::

    System frequency = 250000000 Hz
    l    9   28   36   42   48   54   59   66   72  l   9 19  8  6  6  6  5  7  6
    m    5   14   21   27   34   39   44   51   58  m   5  9  7  6  7  5  5  7  7
    n    6   13   20   25   31   37   43   49   55  n   6  7  7  5  6  6  6  6  6
    o    5   13   19   24   30   36   42   48   54  o   5  8  6  5  6  6  6  6  6
    
    p   27   39   47   55   62   71   78   87   94  p  27 12  8  8  7  9  7  9  7
    q    8   16   24   33   41   50   58   65   74  q   8  8  8  9  8  9  8  7  9
    r    9   18   27   35   43   51   59   66   74  r   9  9  9  8  8  8  8  7  8
    s    8   17   25   33   41   49   57   64   73  s   8  9  8  8  8  8  8  7  9
    
    u    0    3    5    7    9   11   13   15   17  u   0  3  2  2  2  2  2  2  2
    v    0    3    5    7    9   11   13   15   17  v   0  3  2  2  2  2  2  2  2
    w    0    2    4    6    8   10   12   14   16  w   0  2  2  2  2  2  2  2  2
    x    0    2    4    6    8   10   12   14   16  x   0  2  2  2  2  2  2  2  2
    
    System frequency = 125000000 Hz
    l   27   68   80   93  104  117  130  142  154  l  27 41 12 13 11 13 13 12 12
    m   10   24   38   50   63   75   87   98  111  m  10 14 14 12 13 12 12 11 13
    n   11   27   38   50   62   75   86   97  110  n  11 16 11 12 12 13 11 11 13
    o   12   28   39   52   64   77   88  101  113  o  12 16 11 13 12 13 11 13 12
    
    p   21   41   57   73   88  107  122  139  155  p  21 20 16 16 15 19 15 17 16
    q   13   34   50   66   82   99  114  130  145  q  13 21 16 16 16 17 15 16 15
    r   16   35   53   69   88  102  119  135  151  r  16 19 18 16 19 14 17 16 16
    s   17   35   50   67   83   98  114  129  146  s  17 18 15 17 16 15 16 15 17
    
    u    0    7   11   15   19   23   27   31   35  u   0  7  4  4  4  4  4  4  4
    v    1    6   10   14   18   22   26   30   33  v   1  5  4  4  4  4  4  4  3
    w    0    5    9   13   17   21   25   29   33  w   0  5  4  4  4  4  4  4  4
    x    0    5    9   13   17   21   25   29   33  x   0  5  4  4  4  4  4  4  4
    System frequency = 125000000 Hz

The decrease persisted in many subsequent runs, disappearing when I
set `underLimit` and `speedLimit` both to 125000000, and not reliably
reappearing later with other limits.

-------------------

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
