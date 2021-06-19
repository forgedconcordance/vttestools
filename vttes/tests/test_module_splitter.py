import synapse.lib.config as s_config

import synapse.common as s_common


import vttes.tests.common as vt_common

class ModuleSplitterTest(vt_common.VttTstBase):
    def test_character_splitter(self):
        _schema = s_common.jsload('./schema3.json')
        sfunc = s_config.getJsValidator(_schema)

        vault = s_common.jsload('./TFC_Vault_1.json')
        characters = vault.get('characters')
        print(len(characters))
        for c in characters:
            # sfunc(c)
            attrs = c.get('attributes')
            name, archived = attrs.get('name'), attrs.get('archived')
            print(name, archived)

            nstruct = {
                'schema_version': 2,
                'oldId': attrs.get('id'),
                'name': name,
                'avatar': attrs.get('avatar'),
                'bio': c.get('blobBio'),
                'gmnotes': c.get('blobGmNotes'),
                'defaulttoken': c.get('blobDefaultToken'),
                'tags': attrs.get('tags'),
                'controlledby': attrs.get('controlledby'),
                'inplayerjournals': attrs.get('inplayerjournals'),
                'attribs': c.get('attribs'),
                'abilities': c.get('abilities', []),
            }
            sfunc(nstruct)
            s_common.jssave(nstruct, 'v1', f'{name.replace(" ", "_")}.json')
