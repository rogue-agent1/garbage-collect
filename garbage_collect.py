#!/usr/bin/env python3
"""Garbage collector simulator: mark-sweep, reference counting, copying."""
import sys, random

class Object:
    _id = 0
    def __init__(self, size=1, name=None):
        Object._id += 1; self.id = Object._id
        self.name = name or f"obj{self.id}"; self.size = size
        self.refs = []; self.marked = False; self.ref_count = 0

class Heap:
    def __init__(self, capacity=100):
        self.capacity = capacity; self.objects = {}; self.roots = set(); self.used = 0
        self.stats = {"allocated": 0, "freed": 0, "collections": 0}

    def alloc(self, size=1, name=None):
        if self.used + size > self.capacity: return None
        obj = Object(size, name); self.objects[obj.id] = obj
        self.used += size; self.stats["allocated"] += 1; return obj

    def add_ref(self, src, dst):
        if src and dst: src.refs.append(dst.id); dst.ref_count += 1

    def del_ref(self, src, dst):
        if src and dst and dst.id in src.refs:
            src.refs.remove(dst.id); dst.ref_count -= 1

    def add_root(self, obj):
        if obj: self.roots.add(obj.id)

    def del_root(self, obj_id): self.roots.discard(obj_id)

    def mark_sweep(self):
        # Mark phase
        for o in self.objects.values(): o.marked = False
        stack = list(self.roots)
        while stack:
            oid = stack.pop()
            if oid in self.objects and not self.objects[oid].marked:
                self.objects[oid].marked = True
                stack.extend(self.objects[oid].refs)
        # Sweep phase
        dead = [oid for oid, o in self.objects.items() if not o.marked]
        freed = 0
        for oid in dead:
            freed += self.objects[oid].size
            del self.objects[oid]
        self.used -= freed; self.stats["freed"] += len(dead)
        self.stats["collections"] += 1
        return len(dead), freed

    def ref_count_collect(self):
        freed = 0; dead = []
        for oid, o in list(self.objects.items()):
            if o.ref_count == 0 and oid not in self.roots:
                dead.append(oid)
        for oid in dead:
            obj = self.objects[oid]
            for ref_id in obj.refs:
                if ref_id in self.objects: self.objects[ref_id].ref_count -= 1
            freed += obj.size; del self.objects[oid]
        self.used -= freed; self.stats["freed"] += len(dead)
        if dead: self.stats["collections"] += 1
        return len(dead), freed

    def status(self):
        return (f"Heap: {self.used}/{self.capacity} used, {len(self.objects)} objects, "
                f"{len(self.roots)} roots\n"
                f"Stats: {self.stats['allocated']} allocated, {self.stats['freed']} freed, "
                f"{self.stats['collections']} collections")

def demo():
    print("=== Garbage Collector Simulator ===\n")
    h = Heap(50)
    # Allocate objects
    a = h.alloc(5, "A"); h.add_root(a)
    b = h.alloc(3, "B"); h.add_ref(a, b)
    c = h.alloc(4, "C"); h.add_ref(b, c)
    d = h.alloc(2, "D")  # unreachable
    e = h.alloc(6, "E")  # unreachable
    print(f"After allocation: {h.status()}\n")
    dead, freed = h.mark_sweep()
    print(f"Mark-sweep: collected {dead} objects, freed {freed} units")
    print(f"After GC: {h.status()}\n")
    # Remove reference to B
    h.del_ref(a, b)
    dead, freed = h.mark_sweep()
    print(f"After removing A->B: collected {dead} objects, freed {freed} units")
    print(f"Final: {h.status()}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        h = Heap(int(sys.argv[2]) if len(sys.argv) > 2 else 100)
        objs = {}
        print("GC Simulator. Commands: alloc <name> <size>, ref <src> <dst>, root <name>, unroot <name>, gc, status, quit")
        for line in sys.stdin:
            parts = line.strip().split()
            if not parts: continue
            cmd = parts[0]
            if cmd == "alloc":
                o = h.alloc(int(parts[2]) if len(parts)>2 else 1, parts[1])
                if o: objs[parts[1]] = o; print(f"Allocated {parts[1]} (id={o.id})")
                else: print("OOM!")
            elif cmd == "ref": h.add_ref(objs.get(parts[1]), objs.get(parts[2])); print("OK")
            elif cmd == "root": h.add_root(objs.get(parts[1])); print("OK")
            elif cmd == "unroot" and parts[1] in objs: h.del_root(objs[parts[1]].id); print("OK")
            elif cmd == "gc":
                d, f = h.mark_sweep(); print(f"Collected {d} objects, freed {f} units")
            elif cmd == "status": print(h.status())
            elif cmd == "quit": break
    else: demo()

if __name__ == "__main__": main()
