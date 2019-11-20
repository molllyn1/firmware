# (c) Copyright 2018 by Coinkite Inc. This file is part of Coldcard <coldcardwallet.com>
# and is covered by GPLv3 license found in COPYING.
#
# dev_helper.py - Debug and similar code.
#
import ckcc, pyb
from uasyncio import sleep_ms

async def monitor_usb():
    # Provide a helpful message when virtual serial port is connected.
    # Without this, they have to press enter or something to see they are connected.
    from usb import is_vcp_active

    u = pyb.USB_VCP()
    was_connected = u.isconnected()

    while 1:
        await sleep_ms(100)

        conn = u.isconnected()
        if conn and not was_connected:
            # this direct write bypasses vcp_lockdown code.
            if is_vcp_active():
                u.write(b"\r\nWelcome to Coldcard! Press ^C to stop GUI and enter REPL.\r\n")
            else:
                u.write(b"\r\nColdcard developer features disabled.\r\n")

        was_connected = conn
        
async def usb_keypad_emu():
    # Take keypresses on USB virtual serial port (when not in REPL mode)
    # and converts them into keypad events. Super handy for UX testing/dev.
    #
    # IMPORTANT: 
    # - code is **not** used in real product, but left here for devs to use
    # - this code isn't even called; unless you add code to do so, see ../stm32/my_lib_boot2.py
    #
    from ux import the_ux
    from menu import MenuSystem
    from seed import WordNestMenu

    u = pyb.USB_VCP()

    remap = {  '\r': 'y',
             '\x1b': 'x', 
           '\x1b[A': '5', 
           '\x1b[B': '8', 
           '\x1b[C': '9', 
           '\x1b[D': '7' }

    while 1:
        await sleep_ms(100)

        while u.isconnected() and u.any():
            from main import numpad

            k = u.read(3).decode()

            if k in '\x04':     # ^D
                # warm reset
                from machine import soft_reset
                soft_reset()

            if 0:
                if k == 'd':
                    numpad.debug = (numpad.debug + 1) % 3
                    continue

                if k == 'n':
                    if numpad.disabled:
                        numpad.start()
                    else:
                        numpad.stop()

                    print("npdis = %d" % numpad.disabled)
                    continue

            if k == 'U':
                # enter DFU
                import callgate
                callgate.enter_dfu()
                # not reached

            if k == 'T':
                ckcc.vcp_enabled(True)
                print("Repl enabled")
                continue

            if k == 'M':
                import gc
                print("Memory: %d" % gc.mem_free())
                continue

            # word menus: shortcut for first letter
            top = the_ux.top_of_stack()
            if top and isinstance(top, WordNestMenu) and len(top.items) > 6:
                pos = min(len(i.label) for i in top.items)
                if pos >= 2:
                    for n, it in enumerate(top.items):
                        if it.label[pos-2] == k:
                            top.goto_idx(n)
                            top.show()
                            k = None
                            break

                    if k is None: continue

            if k in remap:
                k = remap[k]

            if k in '0123456789xy':
                numpad.inject(k)
                continue
            
            print('? %r' % k)

# EOF
