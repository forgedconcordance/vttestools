import os
import sys
import json
import argparse

import vttes.node as v_node

def main(argv):
    pars = getArgumentParser()
    opts = pars.parse_args(argv)

    print(opts)

    assert os.path.isfile(opts.input)

    with open(opts.input, 'rb') as fd:
        buf = fd.read()

    data = json.loads(buf.decode())
    print(data.keys())
    assert data.get('schema_version') == 1

    mapd = []
    for srcm in data.get('maps', ()):
        attrs = srcm.get('attributes')
        mapd.append({'name': attrs.get('name', 'No Name?'),
                     'id': attrs.get('id'),
                     'archived': attrs.get('archived'),
                     })
    print('Got the following map ids:')
    for mnfo in mapd:
        print(f"{mnfo.get('name')} -> {mnfo.get('archived')}")

    id2info = {}
    for handout in data.get('handouts'):
        attrs = handout.get('attributes')
        id2info[attrs.get('id')] = {'keep': True,
                                    'name': attrs.get('name', 'No Name for Handout?'),
                                    }

    for character in data.get('characters'):
        attrs = character.get('attributes')
        id2info[attrs.get('id')] = {'keep': True,
                                    'name': attrs.get('name', 'No Name for Character?'),
                                    }

    print('Making tree')
    root = v_node.Node(name='Root', idmap=id2info)
    for item in data.get('journal', ()):
        item_id = item.get('id')
        item_path = item.get('path')
        root.addNodePath(item_path, item_id)

    root.pnode(items=True)

    print('*' * 80)
    node = root.addNodePath(('Root', 'Games'))
    node.pnode(level=2, items=True)

    return 0

def getArgumentParser() -> argparse.ArgumentParser:
    pars = argparse.ArgumentParser()
    pars.add_argument('-i', '--input', type=str, required=True,
                      help='input file to filter',
                      )
    return pars

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))