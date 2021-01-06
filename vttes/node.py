from __future__ import annotations

from typing import Tuple

class Node:
    def __init__(self, name: str, parent=None, idmap=None):
        if idmap is None:
            idmap = {}

        self.items = []
        self.leafs = {}
        self.idmap = idmap
        self.name = self.cleanName(name)
        self.parent = parent  # type: Node
        self.path = self.getPath()

    @staticmethod
    def cleanName(name):
        # print(f'iname = {name=}')
        ret = name.replace('.', '_')
        # print(f'oname = {ret=}')
        return ret

    def getPath(self) -> Tuple[str]:
        if self.parent is None:
            return (self.name,)
        path = self.parent.getPath() + (self.name,)
        return path

    def getNode(self, name) -> Node:
        name = self.cleanName(name)
        node = self.leafs.get(name)
        if node:
            return node
        return self.addNode(name)

    def addNode(self, name: str) -> Node:
        name = self.cleanName(name)
        node = Node(name, parent=self, idmap=self.idmap)
        self.leafs[name] = node
        return node

    def getNodePath(self, path, item=None) -> Node:
        # Assumes path is always from the current node.
        assert len(path) > 0, 'Node path must contain 1 or more items.'
        if self.path == path:
            return self
        node = self
        for name in path[1:]:
            node = node.getNode(name)
        if item:
            node.addItem(item)
        return node

    def addItem(self, item) -> None:
        self.items.append(item)

    def __str__(self):
        return f'{self.__class__.__name__} {self.path}'

    def iterNodes(self):
        yield self
        for node in self.leafs.values():
            yield from node.iterNodes()

    def iterItems(self):
        for item in self.items:
            info = self.idmap.get(item, {})
            yield info

    def hasKeepItems(self) -> bool:
        # print(f'hasKeepItems = {str(self)=}')
        for item in self.iterItems():
            if item.get('keep'):
                return True
        for node in self.iterNodes():
            if node is self:
                continue
            if node.hasKeepItems():
                return True
        return False

    def pnode(self, level=0, items=False, cb=print, keep_only=False):
        # print(self, level, items, cb, keep_only)
        hasitem = self.hasKeepItems()
        if keep_only and not hasitem:
            # cb(f'No items kept under the {self.path} node.')
            return

        indent = level * '  '
        cb(f'{indent}{self.name}')
        if items:
            for item in self.items:
                info = self.idmap.get(item, {})
                name = info.get('name', item)
                indx = info.get('indx')
                kxt = '+'
                if not info.get('keep'):
                    if keep_only:
                        continue
                    kxt = '-'
                cb(f'{indent}[{kxt}][{indx}]: {name}')
        for k, v in self.leafs.items():
            v.pnode(level=level + 1, items=items, cb=cb, keep_only=keep_only)
