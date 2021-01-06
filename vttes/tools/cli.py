#!/usr/bin/env python
'''
Tooling to manipulate table exports from vttes/better20
'''
import os
import json
import argparse
import collections

import cmd2
import tabulate

import vttes.node as v_node

speak_parser = argparse.ArgumentParser()
speak_parser.add_argument('-p', '--piglatin', action='store_true', help='atinLay')
speak_parser.add_argument('-s', '--shout', action='store_true', help='N00B EMULATION MODE')
speak_parser.add_argument('-r', '--repeat', type=int, help='output [n] times')
speak_parser.add_argument('words', nargs='+', help='words to say')

load_parser = argparse.ArgumentParser()
load_parser.add_argument('input', type=str,
                         help='input file to filter',
                         )

show_parser = argparse.ArgumentParser()
show_parser_mux = show_parser.add_mutually_exclusive_group()
show_parser_mux.add_argument('-m', '--maps', action='store_true', default=False,
                             help='Show maps')
show_parser_mux.add_argument('-j', '--journal', action='store_true', default=False,
                             help='Show journal')
show_parser.add_argument('-v', '--verbose', default=False, action='store_true',
                         help='Show details')

map_parser = argparse.ArgumentParser()
map_parser.add_argument('action', choices=['list', 'modify'], type=str.lower, default='list',
                        help='action to take.')
map_parser_display_group = map_parser.add_argument_group(title='Display args')
map_parser_display_group.add_argument('-v', '--verbose', default=False, action='store_true',
                                      help='Display all maps, including those which will not be output.')
map_parser_modify_group = map_parser.add_argument_group(title='Modify args')
mpmg_mux = map_parser_modify_group.add_mutually_exclusive_group()
mpmg_mux.add_argument('-e', '--enable', nargs='+', type=int,
                      help='Maps to enabled in output')
mpmg_mux.add_argument('-d', '--disable', nargs='+', type=int,
                      help='Maps to disable in output')

journal_parser = argparse.ArgumentParser()
journal_parser.add_argument('action', choices=['list', 'modify'], type=str.lower, default='list',
                        help='action to take.')
journal_parser.add_argument('-n', '--node', default='Root', action='store', type=str,
                            help='Node to act upon')
journal_parser.add_argument('-i', '--items', nargs='+', type=int, )
journal_parser_display_group = journal_parser.add_argument_group(title='Display args')
journal_parser_display_group.add_argument('-c', '--compact', default=False, action='store_true',
                                          help='Just show the node paths which have items underthem which would be kept.')
journal_parser_display_group.add_argument('-v', '--verbose', default=False, action='store_true',
                                      help='Display all journal items, including those which will not be output.')
journal_parser_modify_group = journal_parser.add_argument_group(title='Modify args')
jpmg_mux = journal_parser_modify_group.add_mutually_exclusive_group()
jpmg_mux.add_argument('-e', '--enable', action='store_true', default=False,
                      help='Journal nodes to enable (including children nodes).')
jpmg_mux.add_argument('-d', '--disable', action='store_true', default=False,
                      help='Journal nodes to disable (including children nodes).')

output_parser = argparse.ArgumentParser()
output_parser.add_argument('outfile', type=str,
                           help='File to write output too.')

class VttES(cmd2.Cmd):

    def __init__(self):
        super().__init__()

        self.current_file = ''
        self.map_data = collections.OrderedDict()
        self.id2info = {}
        self.raw_data = {}
        self.rootnode = v_node.Node(name='Root', idmap=self.id2info)

        # Make maxrepeats settable at runtime
        self.maxrepeats = 3
        self.add_settable(cmd2.Settable('maxrepeats', int, 'max repetitions for speak command'))

    @cmd2.with_argparser(speak_parser)
    def do_speak(self, args):
        """Repeats what you tell me to."""
        words = []
        for word in args.words:
            if args.piglatin:
                word = '%s%say' % (word[1:], word[0])
            if args.shout:
                word = word.upper()
            words.append(word)
        repetitions = args.repeat or 1
        for _ in range(min(repetitions, self.maxrepeats)):
            # .poutput handles newlines, and accommodates output redirection too
            self.poutput(' '.join(words))

    @cmd2.with_argparser(load_parser)
    def do_load(self, args):
        assert os.path.isfile(args.input), f'Input file does not exist {args.input}'
        self.load_from_file(args.input)

    @cmd2.with_argparser(show_parser)
    def do_show(self, args):
        self.poutput(str(args))
        if args.maps:
            for (indx, mnfo) in enumerate(self.map_data):
                self.poutput(f"{mnfo.get('name')} -> {mnfo.get('archived')}")
        if args.journal:
            self.rootnode.pnode(items=args.verbose, cb=self.poutput)

    @cmd2.with_argparser(map_parser)
    def do_map(self, args):
        if args.action == 'list':
            dispdata = []
            if args.verbose:
                for indx, (k, v) in enumerate(self.map_data.items()):
                    obj = {'indx': indx,
                           'name': v.get('name'),
                           'keep': v.get('keep'),
                           'archived': v.get('archived'),
                           'id': k,
                           }
                    dispdata.append(obj)
            else:
                for indx, (k, v) in enumerate(self.map_data.items()):
                    if not v.get('keep'):
                        continue
                    obj = {'indx': indx,
                           'name': v.get('name'),
                           'archived': v.get('archived')}
                    dispdata.append(obj)
            blob = tabulate.tabulate(dispdata,
                                     headers='keys',
                                     tablefmt='psql',
                                     )
            lines = blob.split('\n')
            for line in lines:
                self.poutput(line)

        elif args.action == 'modify':
            mapd = list(self.map_data.values())
            if args.enable:
                for indx in args.enable:
                    obj = mapd[indx]
                    obj['keep'] = True
                    self.poutput(f'Enabled map {obj.get("name")}')
            if args.disable:
                for indx in args.disable:
                    obj = mapd[indx]
                    obj['keep'] = False
                    self.poutput(f'Disabled map {obj.get("name")}')
        else:
            self.poutput(f'unknown action: {args.action}')

    @cmd2.with_argparser(journal_parser)
    def do_journal(self, args):
        path = args.node.split('.')
        if path == self.rootnode.path:
            rnode = self.rootnode
        else:
            rnode = self.rootnode.getNodePath(path)
        self.poutput(f'Working on: {rnode}')
        if args.action == 'list':
            if args.compact:
                # rnode.pnode(items=False, cb=self.poutput, keep_only=False)
                for node in rnode.iterNodes():
                    if not node.hasKeepItems():
                        continue
                    mesg = '.'.join(node.path)
                    self.poutput(f'"{mesg}"')
            elif args.verbose:
                rnode.pnode(items=True, cb=self.poutput)
            else:
                rnode.pnode(items=True, cb=self.poutput, keep_only=True)

        elif args.action == 'modify':
            items = set([d.get('indx') for d in self.id2info.values()])
            if args.enable:
                if args.items:
                    items = set(args.items)

                for node in rnode.iterNodes():
                    for item in node.iterItems():
                        if item.get('indx') in items:
                            if item.get('keep') is True:
                                continue
                            item['keep'] = True
                            self.poutput(f'Keeping {node.path} => {item.get("name")}')
            if args.disable:
                if args.items:
                    items = set(args.items)
                for node in rnode.iterNodes():
                    for item in node.iterItems():
                        if item.get('indx') in items:
                            if item.get('keep') is False:
                                continue
                            item['keep'] = False
                            self.poutput(f'Dropping {node.path} => {item.get("name")}')
        else:
            self.poutput(f'unknown action: {args.action}')

    @cmd2.with_argparser(output_parser)
    def do_output(self, args):
        assert args.outfile.endswith('.json')

        maps = []
        journal = []
        handouts = []
        characters = []
        obj = {
            'schema_version': 1,
            'maps': maps,
            'journal': journal,
            'handouts': handouts,
            'characters': characters,
        }

        for mapd in self.raw_data.get('maps'):
            iden = mapd.get('attributes', {}).get('id')
            info = self.map_data.get(iden)
            if info.get('keep'):
                maps.append(mapd)
        self.poutput(f'Saving {len(maps)} maps.')

        for jrnd in self.raw_data.get('journal'):
            iden = jrnd.get('id')
            if self.id2info.get(iden, {}).get('keep'):
                journal.append(jrnd)


        for hndd in self.raw_data.get('handouts'):
            iden = hndd.get('attributes', {}).get('id')
            if self.id2info.get(iden, {}).get('keep'):
                handouts.append(hndd)
        self.poutput(f'Saving {len(handouts)} handouts.')

        for chrd in self.raw_data.get('characters'):
            iden = chrd.get('attributes', {}).get('id')
            if self.id2info.get(iden, {}).get('keep'):
                characters.append(chrd)
        self.poutput(f'Saving {len(handouts)} characters.')

        self.poutput(f'Writing data to {args.outfile}')
        buf = json.dumps(obj, sort_keys=True, indent=2).encode()
        with open(args.outfile, 'wb') as fd:
            fd.write(buf)

        self.poutput(f'Done writing data!')

    def do_reset(self, args):
        '''
        Reset the current state to the current input file.
        '''
        assert os.path.isfile(self.current_file), f'Current file is not present: {self.current_file}'
        self.load_from_file(self.current_file)

    def load_from_file(self, infile):

        self.poutput(f'Loading data from {infile}')
        with open(infile, 'rb') as fd:
            buf = fd.read()

        data = json.loads(buf.decode())

        assert data.get('schema_version') == 1

        self.current_file = infile
        self.raw_data = data

        self.map_data = collections.OrderedDict()
        for srcm in data.get('maps', ()):
            attrs = srcm.get('attributes')
            mnfo = {'name': attrs.get('name', 'No Name?'),
                    'keep': True,
                    'archived': attrs.get('archived'),
                    }
            self.map_data[attrs.get('id')] = mnfo
        self.poutput(f'Loaded {len(self.map_data)} maps.')

        self.id2info = {}
        indx = 0
        for handout in data.get('handouts'):
            attrs = handout.get('attributes')
            objdata = {'keep': True,
                       'name': attrs.get('name', 'No Name for Handout?'),
                       'indx': indx,
                       'id': attrs.get('id'),
                       }
            indx = indx + 1
            self.id2info[attrs.get('id')] = objdata
        for character in data.get('characters'):
            attrs = character.get('attributes')
            objdata = {'keep': True,
                       'name': attrs.get('name', 'No Name for Character?'),
                       'indx': indx,
                       'id': attrs.get('id'),
                       }
            indx = indx + 1
            self.id2info[attrs.get('id')] = objdata

        self.poutput(f'Loaded {len(self.id2info)} characters and handouts.')

        self.rootnode = v_node.Node(name='Root', idmap=self.id2info)
        for item in data.get('journal', ()):
            item_id = item.get('id')
            item_path = item.get('path')
            self.rootnode.getNodePath(item_path, item_id)

        self.poutput('Loaded Journal Tree')

if __name__ == '__main__':
    import sys
    c = VttES()
    sys.exit(c.cmdloop())
