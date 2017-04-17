#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# ./enum-graphs.py
#
# Copyright (c) 2017 Anssi Yli-Jyrä (author)
#
# Please cite this paper:
#
#   Anssi Yli-Jyrä and Carlos Gómez-Rodriguez
#   Axiomatization of Families of Noncrossing Graph in Dependency Parsing
#   Accepted to ACL 2017, Vancouver.
#
# This program implements a conversion of natural numbers to a corresponding
# unlabeled graph and digraph.  
# This implements methods for printing digraphs or graphs represented by
# the corresponding integers.
# This implements methods for testing OUT, PROJ, ACYCU, ACYCD, ORIENTED, INV, and UNAMBS
# properties of the digraphs.
# This implements a logspace solution to ACYCU.  Similar solutions are prompted
# for curiosity.

# Large graphs require large integers (the number of bits grows in the factorial of the nodes)

# The enumeration of noncrossing graphs is not implemented yet.
# This is silly because there are many more crossing graphs whose
# enumeration and testing takes a lot of time.

# The main loop is a non-cultivated, ad hoc method for enumerating
# (di)graphs and printing reports about them.
# We modified this loop for different purposes, e.g. to enumeration of
# strongly unambiguous graphs, building the ontology and counting
# the cardinality of different categories.

def DFS_connw(underlying,s,accessible):
    if s not in accessible:
        accessible.append(s)
        for e in underlying:
            if s == e[0]:
                DFS_connw(underlying,e[1],accessible)
            elif s == e[1]:
                DFS_connw(underlying,e[0],accessible)
def DFS_cycd(instance, s, todo, rev_topol_order, acyclic_path): # Tarjan's algorithm
    if s in acyclic_path:
        return acyclic_path + [s]   # certificate for cyclicity
    if s in todo:
        for t in [ e[1] for e in instance if e[0] == s ]:
            cyclic_path = DFS_cycd(instance, t, todo, rev_topol_order, acyclic_path + [s])
            if cyclic_path != None:          
                return cyclic_path   
        todo.remove(s)
        rev_topol_order.append(s)     # certificate for acyclicity
    return None
                    
class Template:
    def __init__(self,n,type="graph"):
        self.nodes = n
        self.edges = []
        if type != "graph":
            for i in range(1,n):
                for j in range(i+1,n+1):
                    self.edges = self.edges + [ [i,j], [j,i] ]
        else:
            for i in range(1,n):
                self.edges = self.edges + [ [i,j] for j in range(i+1,n+1) ]
    def print_template(self):
        print(len(self.edges),": ",self.edges)
    def print_instance(self,g,instance = None):
        print(self.make_instance(g,instance))
    def print_underlying(self,g,underlying = None):
        print(self.make_underlying(g,underlying))
    def make_instance(self,digraph_integer,instance = None):
        if instance == None:
            [bit_power, instance] = [1, []]
            for bit in range(0,len(self.edges)):
                if bit_power & digraph_integer != 0:
                    instance.append(self.edges[bit])
                bit_power = bit_power+bit_power
        return instance
    def make_underlying(self,digraph_integer,underlying = None):
        if underlying == None:
            [bit_power, underlying] = [1, []]
            for bit in range(0,len(self.edges),2):
                if (bit_power+bit_power+bit_power) & digraph_integer != 0:
                    underlying.append(self.edges[bit])
                bit_power = bit_power+bit_power+bit_power+bit_power
        return underlying
    def test_inverted(self,g,instance = None):
        instance = self.make_instance(g,instance)
        for e in instance:
            if e[::-1] not in instance:
                return False
        return True
    def test_oriented(self,g,instance = None):
        instance = self.make_instance(g,instance)
        for e in instance:
            if e[::-1] in instance:
                return False
        return True
    def test_out(self,g,instance = None):
        instance = self.make_instance(g,instance)
        indegree = (self.nodes + 1) * [0]
        for e in instance:
            indegree[e[1]] += 1
        for d in indegree:
            if d > 1:
                return False
        return True
    def test_crossing(self,g,underlying = None): # OK
        underlying = self.make_underlying(g,underlying)
        for i in range(0,len(underlying)-1):
            for j in range(i+1,len(underlying)):
                [e,f] = [ underlying[i], underlying[j] ]
                if e[0] < f[0] and f[0] < e[1] and e[1] < f[1]:
                    return 1
        return 0
    def test_projw(self,g,instance = None): # OK
        instance = self.make_instance(g,instance)
        for i in range(0,len(instance)-1):
            for j in range(i+1,len(instance)):
                [e,f] = [ instance[i], instance[j] ]
                if e[0] < e[1] and e[0] == f[1] and e[1] < f[0]:
                    return 0
                if e[1] < e[0] and e[1] == f[0] and e[0] < f[1]:
                    return 0
        return 1
    def test_connw(self,g,underlying = None): # OK
        underlying = self.make_underlying(g,underlying)
        accessible = []   # a variable parameter shared by the whole search three
        if underlying != []:
            DFS_connw(underlying,underlying[0][0],accessible)
        return len(accessible) == self.nodes
    def test_cyclicd(self,g,instance = None): # Tarjan 1976
        instance = self.make_instance(g,instance)
        [todo, rev_topol_order] = [ list(range(1,self.nodes+1)), [] ]   # variable parameters
        while todo != []:
            cyclic_path = DFS_cycd(instance, todo[0], todo, rev_topol_order, [])
            if cyclic_path != None:
                return True
        return False
    def enc_instance(self,g,instance = None):
        instance = self.make_instance(g,instance)
        for i in range(1,self.nodes+1):
            for j in range(i-1,0,-1):
                if [i,j] in instance and [j,i] in instance:
                    print("] ",end="")
                elif [i,j] in instance:
                    print("\\\\ ",end="")
                elif [j,i] in instance:
                    print("> ",end="")
            for j in range(self.nodes,i,-1):
                if [i,j] in instance and [j,i] in instance:
                    print("[ ",end="")
                elif [i,j] in instance:
                    print("/ ",end="")
                elif [j,i] in instance:
                    print("< ",end="")
            if [i,i] in instance:
                print("[] ",end="")
            if i < self.nodes:
                print("{ } ",end="")
    def test_unambs(self,g,instance = None):
        instance = self.make_instance(g,instance)
        for s in range(1,self.nodes+1):
            nonreentrant_order = []
            reentrant_order = DFS_unambs(instance, s, nonreentrant_order, [s])
            if reentrant_order != None:
                return False
        return True
    def test_cyclicu(self,g,underlying = None):
        underlying = self.make_underlying(g,underlying)
        accessible = []   # a variable parameter shared by the whole search three
        if underlying == []:
            return False
        for s in range(1,self.nodes+1):
            if s not in accessible:
                if DFS_cycu(underlying, -1, s, accessible):
                    return True
        return False
    def test_nc_cyclicu(self,g,underlying = None):
        underlying = self.make_underlying(g,underlying)
        for [u,y] in underlying:
            [v,p] = [u,u]
            while p != -1:
                [v,p] = [p,-1]
                for vv in range(v+1,y+1):
                    if [v,vv] in underlying and [v,vv] != [u,y]:
                        if vv == y:
                            return True
                        p = vv
        return False

def DFS_unambs(instance, s, nonreentrant_order, acyclic_path):
    if s in nonreentrant_order:
        return nonreentrant_order + [s]   # certificate for re-entrancy
    nonreentrant_order.append(s)
    for t in [ e[1] for e in instance if e[0] == s ]:
        if t not in acyclic_path:
            reentrant_order = DFS_unambs(instance, t, nonreentrant_order, acyclic_path + [t])
            if reentrant_order != None:   
                return reentrant_order
    return None
    
def DFS_cycu(underlying,parent,s,accessible):
    if s not in accessible:
        accessible.append(s)
        for e in underlying:
            if s == e[0]:
                if (e[1] != parent and e[1] in accessible) or DFS_cycu(underlying,s,e[1],accessible):
                    return True
            elif s == e[1]:
                if (e[0] != parent and e[0] in accessible) or DFS_cycu(underlying,s,e[0],accessible):
                    return True
    return False

# enumerating 3-node digraphs; 6-nodes is still feasible
T = Template(3,"digraph")

for g in range(0,2**len(T.edges)):
    if not T.test_crossing(g):
        acycd = not T.test_cyclicd(g)
        unamb = T.test_unambs(g)
        acycu = not T.test_cyclicu(g)
        nc_acycu = not T.test_nc_cyclicu(g)
        orien = T.test_oriented(g)
        connw = T.test_connw(g)
        out   = T.test_out(g)
        print("XXX ",end="")
        if True:
            if   not acycd and not unamb and not acycu and not orien and not connw and not out:
                print("DIGRAPH", end="")
            elif not acycd and     unamb and not acycu and not orien and not connw and not out:
                print("UNAMB", end="")
            elif not acycd and not unamb and not acycu and not orien and     connw and not out:
                print("CONNW", end="")
            elif not acycd and not unamb and not acycu and     orien and not connw and not out:
                print("ORIENTED", end="")
            elif not acycd and     unamb and not acycu and not orien and not connw and     out:
                print("OUT", end="")
            elif not acycd and     unamb and     acycu and not orien and not connw and not out:
                print("ACYCU=FOREST", end="")
            elif not acycd and     unamb and not acycu and not orien and     connw and not out:
                print("W.C.UNAMB", end="")
            elif not acycd and not unamb and not acycu and     orien and     connw and not out:
                print("W.C.OR.", end="")
            elif     acycd and not unamb and not acycu and     orien and not connw and not out:
                print("ACYCD=DAG", end="")
            elif not acycd and     unamb and not acycu and     orien and not connw and not out:
                print("UNAMB.ORIENTED", end="")
            elif not acycd and     unamb and     acycu and not orien and not connw and     out:
                print("OUT-FOREST", end="")
            elif not acycd and     unamb and     acycu and not orien and     connw and not out:
                print("W.C.FOREST", end="")
            elif not acycd and     unamb and not acycu and     orien and     connw and not out:
                print("W.C.UNAMB.OR.", end="")
            elif     acycd and     unamb and not acycu and     orien and not connw and not out:
                print("MULTITREE", end="")
            elif     acycd and not unamb and not acycu and     orien and     connw and not out:
                print("W.C.DAG", end="")
            elif not acycd and     unamb and not acycu and     orien and not connw and     out:
                print("OUT-ORIENTED", end="")
            elif not acycd and     unamb and not acycu and     orien and     connw and     out:
                print("W.C.OUT-ORIENTED", end="")
            elif not acycd and     unamb and     acycu and not orien and     connw and     out:
                print("W.C.OUT-FOREST", end="")
            elif     acycd and     unamb and     acycu and     orien and not connw and not out:
                print("M.T.FOREST", end="")
            elif     acycd and     unamb and not acycu and     orien and     connw and not out:
                print("W.C.MULTITREE", end="")
            elif     acycd and     unamb and     acycu and     orien and not connw and     out:
                print("OUT-MULTITREE", end="")
            elif     acycd and     unamb and     acycu and     orien and     connw and not out:
                print("POLYTREE", end="")
            elif     acycd and     unamb and     acycu and     orien and     connw and     out:
                print("OUT-TREE", end="")
            else:
                print("ACYCD=",acycd, "U=",unamb, "ACYCU=",acycu, "OR=",orien, "WC=",connw, "OUT=",out)
        print("\t",end="")
        T.enc_instance(g)
        print()
        
