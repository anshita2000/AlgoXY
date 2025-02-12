#!/usr/bin/python

# btree.py, B-Tree
# Copyright (C) 2010, Liu Xinyu (liuxinyu95@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

TREE_2_3_4 = 2 #by default, create 2-3-4 tree

class BTree:
    def __init__(self, d = TREE_2_3_4):
        self.deg = d     # degree
        self.keys = []   # self.data = ...
        self.subtrees = []

def is_leaf(t):
    return t.subtrees == []

def is_full(node):
    return len(node.keys) >= 2 * node.deg - 1

def can_remove(tr):
    return len(tr.keys) >= tr.deg

def replace_key(tr, i, k):
    tr.keys[i] = k
    return k

def merge_subtrees(tr, i):
    #merge subtrees[i] and subtrees[i+1] by pushing keys[i] down
    tr.subtrees[i].keys += [tr.keys[i]] + tr.subtrees[i + 1].keys
    tr.subtrees[i].subtrees += tr.subtrees[i + 1].subtrees
    tr.keys.pop(i)
    tr.subtrees.pop(i + 1)

def split(node, i):
    deg = node.deg
    x = node.subtrees[i]
    y = BTree(deg)
    node.keys.insert(i, x.keys[deg - 1])
    node.subtrees.insert(i + 1, y)
    y.keys = x.keys[deg : ]
    x.keys = x.keys[ : deg - 1]
    if not is_leaf(x):
        y.subtrees = x.subtrees[deg : ]
        x.subtrees = x.subtrees[ : deg]

def insert(tr, key):
    root = tr
    if is_full(root):
        s = BTree(root.deg)
        s.subtrees.insert(0, root)
        split(s, 0)
        root = s
    return insert_nonfull(root, key)

def ordered_insert(lst, x):
    i = len(lst)
    lst.append(x)
    while i > 0 and lst[i] < lst[i - 1]:
        (lst[i - 1], lst[i]) = (lst[i], lst[i - 1])
        i = i - 1

def insert_nonfull(tr, key):
    if is_leaf(tr):
        ordered_insert(tr.keys, key)
    else:
        i = len(tr.keys)
        while i > 0 and key < tr.keys[i-1]:
            i = i - 1
        if is_full(tr.subtrees[i]):
            split(tr, i)
            if key > tr.keys[i]:
                i = i + 1
        insert_nonfull(tr.subtrees[i], key)
    return tr

def B_tree_delete(tr, key):
    i = len(tr.keys)
    while i>0:
        if key == tr.keys[i-1]:
            if is_leaf(tr):  # case 1 in CLRS
                tr.keys.remove(key)
                #disk_write(tr)
            else: # case 2 in CLRS
                if can_remove(tr.subtrees[i-1]): # case 2a
                    key = replace_key(tr, i-1, tr.subtrees[i-1].keys[-1])
                    B_tree_delete(tr.subtrees[i-1], key)
                elif can_remove(tr.subtrees[i]): # case 2b
                    key = replace_key(tr, i-1, tr.subtrees[i].keys[0])
                    B_tree_delete(tr.subtrees[i], key)
                else: # case 2c
                    merge_subtrees(tr, i-1)
                    B_tree_delete(tr.subtrees[i-1], key)
                    if tr.keys==[]: # tree shrinks in height
                        tr = tr.subtrees[i-1]
            return tr
        elif key > tr.keys[i-1]:
            break
        else:
            i = i-1
    # case 3
    if is_leaf(tr):
        return tr #key doesn't exist at all
    if not can_remove(tr.subtrees[i]):
        if i>0 and can_remove(tr.subtrees[i-1]): #left sibling
            tr.subtrees[i].keys.insert(0, tr.keys[i-1])
            tr.keys[i-1] = tr.subtrees[i-1].keys.pop()
            if not is_leaf(tr.subtrees[i]):
                tr.subtrees[i].subtrees.insert(0, tr.subtrees[i-1].subtrees.pop())
        elif i<len(tr.subtrees) and can_remove(tr.subtrees[i+1]): #right sibling
            tr.subtrees[i].keys.append(tr.keys[i])
            tr.keys[i]=tr.subtrees[i+1].keys.pop(0)
            if not is_leaf(tr.subtrees[i]):
                tr.subtrees[i].subtrees.append(tr.subtrees[i+1].subtrees.pop(0))
        else: # case 3b
            if i>0:
                merge_subtrees(tr, i-1)
            else:
                merge_subtrees(tr, i)
    B_tree_delete(tr.subtrees[i], key)
    if tr.keys==[]: # tree shrinks in height
        tr = tr.subtrees[0]
    return tr

def B_tree_search(tr, key):
    for i in range(len(tr.keys)):
        if key<= tr.keys[i]:
            break
    if key == tr.keys[i]:
        return (tr, i)
    if is_leaf(tr):
        return None
    else:
        if key>tr.keys[-1]:
            i=i+1
        #disk_read
        return B_tree_search(tr.subtrees[i], key)

def B_tree_to_str(tr):
    res = "("
    if is_leaf(tr):
        res += ", ".join(tr.keys)
    else:
        for i in range(len(tr.keys)):
            res+= B_tree_to_str(tr.subtrees[i]) + ", " + tr.keys[i] + ", "
        res += B_tree_to_str(tr.subtrees[len(tr.keys)])
    res += ")"
    return res

def list_to_B_tree(l, t=TREE_2_3_4):
    tr = BTree(t)
    for x in l:
        tr = insert(tr, x)
    return tr

class BTreeTest:
    def __init__(self):
        print "B-tree testing"

    def run(self):
        self.test_insert()
        self.test_delete()
        self.test_search()
        #self.__test_insert_verbose()

    def test_insert(self):
        lst = ["G", "M", "P", "X", "A", "C", "D", "E", "J", "K", \
               "N", "O", "R", "S", "T", "U", "V", "Y", "Z"]
        print "2-3-4 tree of", lst
        tr = list_to_B_tree(lst)
        print B_tree_to_str(tr)
        print "B-tree with t=3 of", lst
        print B_tree_to_str(list_to_B_tree(lst, 3))

    def __test_insert_verbose(self):
        lst = ["G", "M", "P", "X", "A", "C", "D", "E", "J", "K", \
               "N", "O", "R", "S", "T", "U", "V", "Y", "Z"]
        for i in range(1, len(lst)):
            print "2-3-4 tree of", lst[:i]
            tr = list_to_B_tree(lst[:i])
            print B_tree_to_str(tr)

    def test_delete(self):
        print "test delete"
        t = 3
        tr = BTree(t)
        tr.keys=["P"]
        tr.subtrees=[BTree(t), BTree(t)]
        tr.subtrees[0].keys=["C", "G", "M"]
        tr.subtrees[0].subtrees=[BTree(t), BTree(t), BTree(t), BTree(t)]
        tr.subtrees[0].subtrees[0].keys=["A", "B"]
        tr.subtrees[0].subtrees[1].keys=["D", "E", "F"]
        tr.subtrees[0].subtrees[2].keys=["J", "K", "L"]
        tr.subtrees[0].subtrees[3].keys=["N", "O"]
        tr.subtrees[1].keys=["T", "X"]
        tr.subtrees[1].subtrees=[BTree(t), BTree(t), BTree(t)]
        tr.subtrees[1].subtrees[0].keys=["Q", "R", "S"]
        tr.subtrees[1].subtrees[1].keys=["U", "V"]
        tr.subtrees[1].subtrees[2].keys=["Y", "Z"]
        print B_tree_to_str(tr)
        lst = ["F", "M", "G", "D", "B", "U"]
        reduce(self.__test_del__, lst, tr)

    def __test_del__(self, tr, key):
        print "delete", key
        tr = B_tree_delete(tr, key)
        print B_tree_to_str(tr)
        return tr

    def test_search(self):
        lst = ["G", "M", "P", "X", "A", "C", "D", "E", "J", "K", \
               "N", "O", "R", "S", "T", "U", "V", "Y", "Z"]
        tr = list_to_B_tree(lst, 3)
        print "test search\n", B_tree_to_str(tr)
        for i in lst:
            self.__test_search__(tr, i)
        self.__test_search__(tr, "W")

    def __test_search__(self, tr, k):
        res = B_tree_search(tr, k)
        if res is None:
            print k, "not found"
        else:
            (node, i) = res
            print "found", node.keys[i]

if __name__ == "__main__":
    BTreeTest().run()
