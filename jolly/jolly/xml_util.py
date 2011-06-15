"""Dump canonical objects to XML."""

from __future__ import absolute_import # so we don't try to import ourself

def dumps(object):
    """Dumps a canonical object to an XML string."""
    import xml.etree.ElementTree as ET
    for k, v in object.iteritems(): # there should only be one
        fn = _mapping.get(type(v), _dump_default)
        node = fn([], k, v)
        return ET.tostring(node)
    return ''

def _dump_dict(root, name, object):
    """Update ElementTree root with dict object."""
    import xml.etree.ElementTree as ET
    node = ET.Element(name)
    for k, v in object.iteritems():
        fn = _mapping.get(type(v), _dump_default)
        fn(node, k, v)
    return node
     
def _dump_seq(root, name, object):
    """Update ElementTree root with sequence object."""
    import xml.etree.ElementTree as ET
    node = ET.Element(name)
    for o in object:
        for k, v in o.iteritems():
            node.append(_dump_dict(node, k, v))
    root.append(node)
    return node

def _dump_default(root, name, object):
    """Update ElementTree root with object attribute."""
    root.set(name, str(object))
    return root

_mapping = {dict: _dump_dict, list: _dump_seq, tuple: _dump_seq}
