# -*- mode: python;  coding: utf-8 -*-  jiw - 28 Dec 2024
#  getPIOcodes decodes an assembled PIO State Machine for RP2040

import rp2
# Put your PIO program, called pioProg, here ...
# Following is not a meaningful program; is just for testing decode
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def pioProg():
    set(pins, 1)                # p0
    set(pins, 0)
    set(pins, 1)
    set(pins, 0) [7]
    set(pins, 0)                # p4
    set(pins, 1) [5]
    #wrap()
    set(pins, 1)                # p6
    label('hiTop')  # Store y & x, as either fallen-count or up-noise
    mov(isr, y)                 # p7
    push(noblock)               # p8
    wrap_target()
    wrap()
    pull(block)                 # p9
    mov(isr, invert(x))         # p10
    push(noblock)               # Push time-count
    label('waitHi')             # Loop to await rising edge
    jmp(pin, 'hiUp')            # Got a rising edge?
    jmp(x_dec, 'waitHi')        # Count 1 clock
    jmp(x_dec, 'waitHi')        # p14
    jmp('waitHi')               # in case x==0
    label('hiUp')               # Pin was set, see if it stays so
    nop() [13]                  # p16
    jmp(y_dec, 'hiTop')         # p17

# Note - When asm_pio treats wrap(), it doesn't check if wrap()
# already occurred.  Just OR's new value -1 into ExecCtrl word at
# self.prog[_PROG_EXECCTRL].  Also doesn't check if wrap() precedes
# wrap_target(), if that matters.  See def wrap_target(self): and def
# wrap(self): in file micropython/ports/rp2/modules/p2.py

def decode(v):
    def f(bb, nb):  return (v>>bb) & ((1<<nb)-1)
    op  = f(13,3)
    dss = f(8,5)
    cnd=ins=dst=etc=f(5,3) # jmp cond; wait P/S; in S; dst for 3 ops; ...
    wss = etc&3                 # for wait
    pbit= (etc&4)//4            # for push, pull, irq, wait 
    fbit= (etc&2)//2            # for push, pull, irq
    bbit= etc&1                 # for push, pull, irq
    num = f(0,5)
    mop = f(3,2)                # `op` code for `mov`
    src = f(0,3)                # `src` for `mov`
    # Build text string for the instruction
    tcnd  =  ('','!x','x--','!y' ,'y--'  ,'x!=y' ,'pin','!osre')[cnd]
    tins  = ('pins','x','y','nul','res'  ,'res'  ,'isr','osr')[etc]
    tdsto = ('pins','x','y','nul','pindirs','pc' ,'isr','exec')[dst]
    tdstm = ('pins','x','y','res','exec' ,'pc'   ,'isr','osr')[dst]
    tdsts = ('pins','x','y','res','pindirs','res','res','res')[dst]
    topm  = ('','inv','reverse','res')[mop]
    tsrcm = ('pins','x','y','nul','res' ,'status','isr','osr')[src]
    # Build text of decoded instruction
    def twait():
        return ('0','1')[pbit]+' '+('gpio','pin','irq','res')[etc&3]
    def tpupu():
        return ('', ('IfFull','IfEmpty')[pbit])[fbit] + f"{('No','')[bbit]}Block"
    oj, ow, oi, oo, opu, om, oq, os = range(8)
    top  = ('jmp','wait','in','out','pupu','mov','irq','set')[op]
    if op==opu: top = 'pull' if etc>3 else 'push'
    f2 =  f'{tcnd} p{num}' if op==oj else twait if op==ow else tins if op==oi else tdsto if op==oo else tpupu() if op==opu else f'{tdstm}, {topm} {tsrcm}' if op==om else f'{("","clear")[fbit]} {("","wait")[bbit]}' if op==oq else f'{tdsts}, {num}'
    f3 = f'[{dss}]' if dss else ''
    return f'{top:4} {f2} {f3}'
    
p=pioProg[0]
xc=pioProg[3]
wrap_target = (xc>>7)&31
wrap =(xc>>12)&31
print(f'{p=}');  print()
print(f'execCtrl={xc:X} :  wrap@{wrap:02X}x {wrap}  wrapTo:{wrap_target}');  print()
#print(f'{pioProg=}');  print()
for j, v in enumerate(p):
    print(f'p{j:<2d}   {v:04x}   {decode(v):22}')
