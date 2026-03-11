#!/usr/bin/env python3
"""Mark-and-sweep garbage collector simulation."""
import sys
class Obj:
    _all=[]
    def __init__(self,name,refs=None):
        self.name,self.refs,self.marked=name,refs or [],False; Obj._all.append(self)
    def __repr__(self): return self.name
def mark(roots):
    stack=list(roots)
    while stack:
        obj=stack.pop()
        if not obj.marked: obj.marked=True; stack+=obj.refs
def sweep():
    alive=[o for o in Obj._all if o.marked]
    dead=[o for o in Obj._all if not o.marked]
    Obj._all=alive
    for o in alive: o.marked=False
    return dead
# Demo
a,b,c,d,e=Obj('A'),Obj('B'),Obj('C'),Obj('D'),Obj('E')
a.refs=[b,c]; b.refs=[c]; c.refs=[]; d.refs=[e]; e.refs=[d]  # D-E are a cycle
roots=[a]
print(f"All objects: {Obj._all}")
print(f"Roots: {roots}")
mark(roots); dead=sweep()
print(f"Collected: {dead}")
print(f"Alive: {Obj._all}")
