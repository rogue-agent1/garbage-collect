#!/usr/bin/env python3
"""Mark-and-sweep garbage collector simulation."""
class Object:
    _id=0
    def __init__(self,name=None):
        Object._id+=1;self.id=Object._id;self.name=name or f"obj{self.id}"
        self.refs=[];self.marked=False
    def add_ref(self,other): self.refs.append(other)
    def __repr__(self): return self.name
class Heap:
    def __init__(self): self.objects=[];self.roots=set()
    def alloc(self,name=None):
        obj=Object(name);self.objects.append(obj);return obj
    def add_root(self,obj): self.roots.add(obj)
    def remove_root(self,obj): self.roots.discard(obj)
    def gc(self):
        for obj in self.objects: obj.marked=False
        for root in self.roots: self._mark(root)
        before=len(self.objects)
        freed=[o for o in self.objects if not o.marked]
        self.objects=[o for o in self.objects if o.marked]
        return freed
    def _mark(self,obj):
        if obj.marked: return
        obj.marked=True
        for ref in obj.refs: self._mark(ref)
class RefCountGC:
    def __init__(self): self.objects={};self.refcounts={}
    def alloc(self,name=None):
        obj=Object(name);self.objects[obj.id]=obj;self.refcounts[obj.id]=1;return obj
    def inc_ref(self,obj): self.refcounts[obj.id]+=1
    def dec_ref(self,obj):
        self.refcounts[obj.id]-=1
        if self.refcounts[obj.id]<=0:
            for ref in obj.refs: self.dec_ref(ref)
            del self.objects[obj.id];del self.refcounts[obj.id];return True
        return False
if __name__=="__main__":
    h=Heap()
    a=h.alloc("A");b=h.alloc("B");c=h.alloc("C");d=h.alloc("D")
    a.add_ref(b);b.add_ref(c)
    h.add_root(a)
    freed=h.gc()
    assert d in freed and len(h.objects)==3
    print(f"Mark-sweep: freed {[str(o) for o in freed]}, alive {[str(o) for o in h.objects]}")
    rc=RefCountGC();x=rc.alloc("X");y=rc.alloc("Y");x.add_ref(y);rc.inc_ref(y)
    rc.dec_ref(y);assert y.id in rc.objects
    rc.dec_ref(x);assert x.id not in rc.objects
    print("GC simulation OK")
