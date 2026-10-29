#!/usr/bin/env python3
"""Side-channel breakpoint control for the live r5c session (second WS
client): usage: bp_side.py list | remove <hexaddr> | add <hexaddr>"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ws_trace import WS, Debugger

ws = WS('127.0.0.1', 54809)
dbg = Debugger(ws)
cmd = sys.argv[1]
if cmd == 'list':
    print(json.dumps(dbg.request({'event': 'cpu.breakpoint.list'}), indent=1)[:2000])
elif cmd == 'remove':
    addr = int(sys.argv[2], 16)
    print('remove:', dbg.request({'event': 'cpu.breakpoint.remove', 'address': addr}))
    print(json.dumps(dbg.request({'event': 'cpu.breakpoint.list'}))[:1000])
elif cmd == 'add':
    addr = int(sys.argv[2], 16)
    print('add:', dbg.request({'event': 'cpu.breakpoint.add', 'address': addr, 'enabled': True}))
    print(json.dumps(dbg.request({'event': 'cpu.breakpoint.list'}))[:1000])
