# -*- mode: python;  coding: utf-8 -*-  jiw - 23 Dec 2024, 20 Jan 2025

#  makeCounters.py -- Has PIO State Machine code for several splits of
#  the 11 decrement instructions that follow data storage in
#  calibratePulse8b.  An example of use is shown next, in which k is
#  the number of decrements to be selected after falling edge data is
#  stored.  Values of k from 4 to 7 are allowed.

#   from makeCounters import makeCounter
#   cpio = makeCounter(k)
#   csm = StateMachine(7, cpio, freq=counterFreq, jmp_pin=pini)

def makeCounter(k):
    from rp2 import asm_pio, PIO
    #-----------------------------------------------------------
    GRise=const(1)         # Data item = rising-edge time
    GFall=const(0)         # Data item = falling-edge time
    GStart=const(2)        # Data item = unused item
    #---------------------------------------------------------------
    #--------Define Counter State machine 0, to time edges----------
    #--------------------------------------------------------------
    @asm_pio(fifo_join=PIO.JOIN_RX)  # Use both 4-fifos as 1 8-fifo
    def counter3():
        set(y, GFall)             # We await a falling edge
        mov(x, invert(y))         # Start x at ~0
        label('0'); jmp(pin, "1") # Wait for high level.
        jmp('0')    # This loop out due to OSError: [Errno 12] ENOMEM
        label('1'); jmp(pin, "1") # Wait for low level, then fall thru
        wrap_target()
        #------------Save falling-edge time-------------------
        mov(isr, y)               # Load mark-code y 
        push(noblock)             # Push mark-code: GFall
        mov(isr, invert(x))       # Load falling-edge time ~x
        push(noblock)             # Push falling-edge time
        #------------Do time catch-up for missed counts--------
        jmp(x_dec, 'a'); label('a')
        jmp(x_dec, 'b'); label('b') # After falling edge,
        jmp(x_dec, 'c'); label('c') # Do catch-up x_dec's
        #---------------Await rising edge-----------------------
        label("waitHi")            # Loop: a
        jmp(pin, "HaveHi")         # Got a rising edge?
        jmp(x_dec, "waitHi")       # Count 1 clock
        jmp("waitHi")              # in case x==0
        #---------------Save rising-edge time--------------------
        label("HaveHi")
        set(y,GRise)                # Save rising-edge time
        mov(isr, y)
        push(noblock)               # Push mark-code, GRise
        mov(isr, invert(x))
        push(noblock)               # Push rising-edge time
        #------------Do time catch-up for missed counts-----------
        jmp(x_dec, 'd'); label('d')
        jmp(x_dec, 'e'); label('e')
        jmp(x_dec, 'f'); label('f')
        jmp(x_dec, 'g'); label('g')
        jmp(x_dec, 'p'); label('p')
        jmp(x_dec, 'q'); label('q') # After rising edge,
        jmp(x_dec, 'r'); label('r') # do catch-up x_dec's
        jmp(x_dec, 's'); label('s')
        #---------------Await falling edge------------------------
        label("waitLo")
        jmp(x_dec, "-"); label("-") # x_dec to count 1 clock
        jmp(pin, "waitLo")          # Loop if pin is up
        #--------------Pin fell, go save falling-edge time--------
        set(y,GFall)   # Wrap to top to save GFall entry
        wrap()
    #---------------------------------------------------------------
    @asm_pio(fifo_join=PIO.JOIN_RX)  # Use both 4-fifos as 1 8-fifo
    def counter4():
        set(y, GFall)             # We await a falling edge
        mov(x, invert(y))         # Start x at ~0
        label('0'); jmp(pin, "1") # Wait for high level.
        jmp('0')    # This loop out due to OSError: [Errno 12] ENOMEM
        label('1'); jmp(pin, "1") # Wait for low level, then fall thru
        wrap_target()
        #------------Save falling-edge time-------------------
        mov(isr, y)               # Load mark-code y 
        push(noblock)             # Push mark-code: GFall
        mov(isr, invert(x))       # Load falling-edge time ~x
        push(noblock)             # Push falling-edge time
        #------------Do time catch-up for missed counts--------
        jmp(x_dec, 'a'); label('a')
        jmp(x_dec, 'b'); label('b') # After falling edge,
        jmp(x_dec, 'c'); label('c') # Do catch-up x_dec's
        jmp(x_dec, 'd'); label('d')
        #---------------Await rising edge-----------------------
        label("waitHi")            # Loop: a
        jmp(pin, "HaveHi")         # Got a rising edge?
        jmp(x_dec, "waitHi")       # Count 1 clock
        jmp("waitHi")              # in case x==0
        #---------------Save rising-edge time--------------------
        label("HaveHi")
        set(y,GRise)                # Save rising-edge time
        mov(isr, y)
        push(noblock)               # Push mark-code, GRise
        mov(isr, invert(x))
        push(noblock)               # Push rising-edge time
        #------------Do time catch-up for missed counts-----------
        jmp(x_dec, 'p'); label('p')
        jmp(x_dec, 'q'); label('q') # After rising edge,
        jmp(x_dec, 'r'); label('r') # do catch-up x_dec's
        jmp(x_dec, 's'); label('s')
        jmp(x_dec, 't'); label('t')
        jmp(x_dec, 'u'); label('u')
        jmp(x_dec, 'v'); label('v')
        #---------------Await falling edge------------------------
        label("waitLo")
        jmp(x_dec, "-"); label("-") # x_dec to count 1 clock
        jmp(pin, "waitLo")          # Loop if pin is up
        #--------------Pin fell, go save falling-edge time--------
        set(y,GFall)   # Wrap to top to save GFall entry
        wrap()
    #--------------------------------------------------------------
    @asm_pio(fifo_join=PIO.JOIN_RX)  # Use both 4-fifos as 1 8-fifo
    def counter5():
        set(y, GFall)             # We await a falling edge
        mov(x, invert(y))         # Start x at ~0
        label('0'); jmp(pin, "1") # Wait for high level.
        jmp('0')    # This loop out due to OSError: [Errno 12] ENOMEM
        label('1'); jmp(pin, "1") # Wait for low level, then fall thru
        wrap_target()
        #------------Save falling-edge time-------------------
        mov(isr, y)               # Load mark-code y 
        push(noblock)             # Push mark-code: GFall
        mov(isr, invert(x))       # Load falling-edge time ~x
        push(noblock)             # Push falling-edge time
        #------------Do time catch-up for missed counts--------
        jmp(x_dec, 'a'); label('a')
        jmp(x_dec, 'b'); label('b') # After falling edge,
        jmp(x_dec, 'c'); label('c') # Do catch-up x_dec's
        jmp(x_dec, 'd'); label('d')
        jmp(x_dec, 'e'); label('e')
        #---------------Await rising edge-----------------------
        label("waitHi")            # Loop: a
        jmp(pin, "HaveHi")         # Got a rising edge?
        jmp(x_dec, "waitHi")       # Count 1 clock
        jmp("waitHi")              # in case x==0
        #---------------Save rising-edge time--------------------
        label("HaveHi")
        set(y,GRise)                # Save rising-edge time
        mov(isr, y)
        push(noblock)               # Push mark-code, GRise
        mov(isr, invert(x))
        push(noblock)               # Push rising-edge time
        #------------Do time catch-up for missed counts-----------
        jmp(x_dec, 'p'); label('p')
        jmp(x_dec, 'q'); label('q') # After rising edge,
        jmp(x_dec, 'r'); label('r') # do catch-up x_dec's
        jmp(x_dec, 's'); label('s')
        jmp(x_dec, 't'); label('t')
        jmp(x_dec, 'u'); label('u')
        #---------------Await falling edge------------------------
        label("waitLo")
        jmp(x_dec, "-"); label("-") # x_dec to count 1 clock
        jmp(pin, "waitLo")          # Loop if pin is up
        #--------------Pin fell, go save falling-edge time--------
        set(y,GFall)   # Wrap to top to save GFall entry
        wrap()
    #--------------------------------------------------------------
    @asm_pio(fifo_join=PIO.JOIN_RX)  # Use both 4-fifos as 1 8-fifo
    def counter6():
        set(y, GFall)             # We await a falling edge
        mov(x, invert(y))         # Start x at ~0
        label('0'); jmp(pin, "1") # Wait for high level.
        jmp('0')    # This loop out due to OSError: [Errno 12] ENOMEM
        label('1'); jmp(pin, "1") # Wait for low level, then fall thru
        wrap_target()
        #------------Save falling-edge time-------------------
        mov(isr, y)               # Load mark-code y 
        push(noblock)             # Push mark-code: GFall
        mov(isr, invert(x))       # Load falling-edge time ~x
        push(noblock)             # Push falling-edge time
        #------------Do time catch-up for missed counts--------
        jmp(x_dec, 'a'); label('a')
        jmp(x_dec, 'b'); label('b') # After falling edge,
        jmp(x_dec, 'c'); label('c') # Do catch-up x_dec's
        jmp(x_dec, 'd'); label('d')
        jmp(x_dec, 'e'); label('e')
        jmp(x_dec, 'f'); label('f')
        #---------------Await rising edge-----------------------
        label("waitHi")            # Loop: a
        jmp(pin, "HaveHi")         # Got a rising edge?
        jmp(x_dec, "waitHi")       # Count 1 clock
        jmp("waitHi")              # in case x==0
        #---------------Save rising-edge time--------------------
        label("HaveHi")
        set(y,GRise)                # Save rising-edge time
        mov(isr, y)
        push(noblock)               # Push mark-code, GRise
        mov(isr, invert(x))
        push(noblock)               # Push rising-edge time
        #------------Do time catch-up for missed counts-----------
        jmp(x_dec, 'p'); label('p')
        jmp(x_dec, 'q'); label('q') # After rising edge,
        jmp(x_dec, 'r'); label('r') # do catch-up x_dec's
        jmp(x_dec, 's'); label('s')
        jmp(x_dec, 't'); label('t')
        #---------------Await falling edge------------------------
        label("waitLo")
        jmp(x_dec, "-"); label("-") # x_dec to count 1 clock
        jmp(pin, "waitLo")          # Loop if pin is up
        #--------------Pin fell, go save falling-edge time--------
        set(y,GFall)   # Wrap to top to save GFall entry
        wrap()
    #--------------------------------------------------------------
    @asm_pio(fifo_join=PIO.JOIN_RX)  # Use both 4-fifos as 1 8-fifo
    def counter7():
        set(y, GFall)             # We await a falling edge
        mov(x, invert(y))         # Start x at ~0
        label('0'); jmp(pin, "1") # Wait for high level.
        jmp('0')    # This loop out due to OSError: [Errno 12] ENOMEM
        label('1'); jmp(pin, "1") # Wait for low level, then fall thru
        wrap_target()
        #------------Save falling-edge time-------------------
        mov(isr, y)               # Load mark-code y 
        push(noblock)             # Push mark-code: GFall
        mov(isr, invert(x))       # Load falling-edge time ~x
        push(noblock)             # Push falling-edge time
        #------------Do time catch-up for missed counts--------
        jmp(x_dec, 'a'); label('a')
        jmp(x_dec, 'b'); label('b') # After falling edge,
        jmp(x_dec, 'c'); label('c') # Do catch-up x_dec's
        jmp(x_dec, 'd'); label('d')
        jmp(x_dec, 'e'); label('e')
        jmp(x_dec, 'f'); label('f')
        jmp(x_dec, 'g'); label('g')
        #---------------Await rising edge-----------------------
        label("waitHi")            # Loop: a
        jmp(pin, "HaveHi")         # Got a rising edge?
        jmp(x_dec, "waitHi")       # Count 1 clock
        jmp("waitHi")              # in case x==0
        #---------------Save rising-edge time--------------------
        label("HaveHi")
        set(y,GRise)                # Save rising-edge time
        mov(isr, y)
        push(noblock)               # Push mark-code, GRise
        mov(isr, invert(x))
        push(noblock)               # Push rising-edge time
        #------------Do time catch-up for missed counts-----------
        jmp(x_dec, 'p'); label('p')
        jmp(x_dec, 'q'); label('q') # After rising edge,
        jmp(x_dec, 'r'); label('r') # do catch-up x_dec's
        jmp(x_dec, 's'); label('s')
        #---------------Await falling edge------------------------
        label("waitLo")
        jmp(x_dec, "-"); label("-") # x_dec to count 1 clock
        jmp(pin, "waitLo")          # Loop if pin is up
        #--------------Pin fell, go save falling-edge time--------
        set(y,GFall)   # Wrap to top to save GFall entry
        wrap()
    #--------------------------------------------------------------
    @asm_pio(fifo_join=PIO.JOIN_RX)  # Use both 4-fifos as 1 8-fifo
    def counter8():
        set(y, GFall)             # We await a falling edge
        mov(x, invert(y))         # Start x at ~0
        label('0'); jmp(pin, "1") # Wait for high level.
        jmp('0')    # This loop out due to OSError: [Errno 12] ENOMEM
        label('1'); jmp(pin, "1") # Wait for low level, then fall thru
        wrap_target()
        #------------Save falling-edge time-------------------
        mov(isr, y)               # Load mark-code y 
        push(noblock)             # Push mark-code: GFall
        mov(isr, invert(x))       # Load falling-edge time ~x
        push(noblock)             # Push falling-edge time
        #------------Do time catch-up for missed counts--------
        jmp(x_dec, 'a'); label('a')
        jmp(x_dec, 'b'); label('b') # After falling edge,
        jmp(x_dec, 'c'); label('c') # Do catch-up x_dec's
        jmp(x_dec, 'd'); label('d')
        jmp(x_dec, 'e'); label('e')
        jmp(x_dec, 'f'); label('f')
        jmp(x_dec, 'g'); label('g')
        jmp(x_dec, 'h'); label('h')
        #---------------Await rising edge-----------------------
        label("waitHi")            # Loop: a
        jmp(pin, "HaveHi")         # Got a rising edge?
        jmp(x_dec, "waitHi")       # Count 1 clock
        jmp("waitHi")              # in case x==0
        #---------------Save rising-edge time--------------------
        label("HaveHi")
        set(y,GRise)                # Save rising-edge time
        mov(isr, y)
        push(noblock)               # Push mark-code, GRise
        mov(isr, invert(x))
        push(noblock)               # Push rising-edge time
        #------------Do time catch-up for missed counts-----------
        jmp(x_dec, 'p'); label('p')
        jmp(x_dec, 'q'); label('q') # After rising edge,
        jmp(x_dec, 'r'); label('r') # do catch-up x_dec's
        #---------------Await falling edge------------------------
        label("waitLo")
        jmp(x_dec, "-"); label("-") # x_dec to count 1 clock
        jmp(pin, "waitLo")          # Loop if pin is up
        #--------------Pin fell, go save falling-edge time--------
        set(y,GFall)   # Wrap to top to save GFall entry
        wrap()
    #-------------------------------------------------------------
    if 3 <= k <= 8:
        return (counter3, counter4, counter5,
                counter6, counter7, counter8)[k-3]
    else:
        print('Invalid counter-split {k}');  sys.exit()
    #-------------------------------------------------------------
