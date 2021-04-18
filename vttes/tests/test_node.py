import vttes.tests.common as vt_common

import vttes.node as v_node

class NodeTests(vt_common.VttTstBase):
    def test_node(self):
        root = v_node.Node(name='Root')
        self.isinstance(root, v_node.Node)  # TODO Placeholder test

    def test_tree(self):
        root = v_node.Node(name='Root')
        child1 = v_node.Node(name='Child1', parent=root)  # TODO Use this
        child2 = v_node.Node(name='Child2', parent=root)
        grandchild21 = v_node.Node(name='GrandChild21', parent=child2)
        self.eq(str(grandchild21), "Node ('Root', 'Child2', 'GrandChild21')")
