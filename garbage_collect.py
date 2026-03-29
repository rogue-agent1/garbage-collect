#!/usr/bin/env python3
"""GC simulator: mark-sweep, copying, generational, reference counting."""
import sys

class Object:
    _id = 0
    def __init__(self, size=1):
        Object._id += 1; self.id = Object._id
        self.size = size; self.refs = []; self.marked = False; self.gen = 0; self.ref_count = 0

class MarkSweep:
    def __init__(self): self.heap = []; self.roots = set()
    def alloc(self, size=1):
        obj = Object(size); self.heap.append(obj); return obj
    def add_root(self, obj): self.roots.add(obj.id)
    def collect(self):
        for obj in self.heap: obj.marked = False
        # Mark
        stack = [o for o in self.heap if o.id in self.roots]
        while stack:
            obj = stack.pop()
            if not obj.marked:
                obj.marked = True
                stack.extend(obj.refs)
        # Sweep
        freed = [o for o in self.heap if not o.marked]
        self.heap = [o for o in self.heap if o.marked]
        return len(freed)

class GenerationalGC:
    def __init__(self):
        self.young = []; self.old = []; self.roots = set()
        self.promote_threshold = 3
    def alloc(self, size=1):
        obj = Object(size); self.young.append(obj); return obj
    def minor_collect(self):
        # Mark from roots
        for obj in self.young + self.old: obj.marked = False
        stack = [o for o in self.young+self.old if o.id in self.roots]
        while stack:
            obj = stack.pop()
            if not obj.marked: obj.marked = True; stack.extend(obj.refs)
        promoted = freed = 0
        new_young = []
        for obj in self.young:
            if obj.marked:
                obj.gen += 1
                if obj.gen >= self.promote_threshold: self.old.append(obj); promoted += 1
                else: new_young.append(obj)
            else: freed += 1
        self.young = new_young
        return freed, promoted

def main():
    gc = MarkSweep()
    a = gc.alloc(10); b = gc.alloc(20); c = gc.alloc(30)
    a.refs.append(b); gc.add_root(a)
    freed = gc.collect()
    print(f"Mark-Sweep: freed {freed} objects, {len(gc.heap)} alive")

    ggc = GenerationalGC()
    objs = [ggc.alloc(i) for i in range(10)]
    ggc.roots = {objs[0].id, objs[3].id}; objs[0].refs.append(objs[1])
    freed, promoted = ggc.minor_collect()
    print(f"Generational: freed {freed}, promoted {promoted}, young={len(ggc.young)}, old={len(ggc.old)}")

if __name__ == "__main__": main()
