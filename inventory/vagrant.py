#!/usr/bin/python

import os
import re
import json

def inventory_path():
    script_basepath = os.path.dirname(os.path.abspath(__file__))
    inventory_relpath = os.path.join(*"../.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory".split('/'))
    inventory_fulpath = os.path.join(script_basepath, inventory_relpath)
    return(inventory_fulpath)

def build_json_inventory(raw_lines):
    content_lines = [ x.strip() for x in raw_lines]
    pruned_lines = [x for x in content_lines if not x == "" and not x.startswith('#')]
    sections = build_sections(pruned_lines)
    output = []
    meta = []
    for section in sections:
        if isinstance(section, basestring):
            output.append(build_section_host_output(section)) 
            meta.append(build_section_meta_output(section))
        elif isinstance(section, list):
            output.append(build_section_group_output(section))
        else:
            assert False, "Unrecognized object {0}".format(section)
    output.append(('_meta', { 'hostvars': dict(meta) }))
    return json.dumps(dict(output))

def build_section_host_output(line):
    name = line.split(' ')[0]
    return (name, [name])

def build_section_meta_output(line):
    name = line.split(' ')[0]
    attrs = line.split(' ')[1:] + ["ansible_ssh_user=vagrant"]
    return (name, dict([tuple(x.split('=')) for x in attrs]))

def build_section_group_output(params):
    if not re.search("children", params[0]):
        name = re.sub("[\[\]]", '', params[0])
        result = (name , params[1:])
    else:
        name = re.sub(":children", '', params[0])
        name = re.sub("[\[\]]", '', name)
        result = (name, dict([('children', params[1:])]))
    return result
    
def build_sections(lines):
    sections = None
    cursection = list()
    for line in lines:
        if line.startswith('['):
            if sections is None:
                sections = cursection
            else: 
                sections.append(cursection)
            cursection = list()
        cursection.append(line)
    if sections is None:
        sections = cursection
    else: 
        sections.append(cursection)
    return sections    

def empty_json_inventory():
    return "{ }"

if (os.path.isfile(inventory_path())):
    with open(inventory_path()) as inventory:
        output = build_json_inventory(inventory.readlines())
else:
    output = empty_json_inventory()
print(output)