import vttes.tests.common as vt_common

import vttes.node as v_node

class NodeTests(vt_common.VttTstBase):
    def test_node(self):
        root = v_node.Node(name='Root')
        self.isinstance(root, v_node.Node)  # Placeholder test
