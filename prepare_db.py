# -*- coding: utf-8 -*-
#==============================================================================
# ## Shape Element Function
# The function takes as input an iterparse Element object and return a dictionary.
# 
# ### If the element top level tag is "node":
# The dictionary returns the format {"node": .., "node_tags": ...}
# 
# The "node" field holds a dictionary of the following top level node attributes:
# - id
# - user
# - uid
# - version
# - lat
# - lon
# - timestamp
# - changeset
# All other attributes are ignored
# 
# The "node_tags" field holds a list of dictionaries, one per secondary tag. Secondary tags are
# child tags of node which have the tag name/type: "tag". Each dictionary should have the following
# fields from the secondary tag attributes:
# - id: the top level node id attribute value
# - key: the full tag "k" attribute value if no colon is present or the characters after the colon if one is.
# - value: the tag "v" attribute value
# - type: either the characters before the colon in the tag "k" value or "regular" if a colon
#         is not present.
# 
# Additionally,
# 
# - if the tag "k" value contains problematic characters, the tag  is ignored
# - if the tag "k" value contains a ":" the characters before the ":" is set as the tag type
#   and characters after the ":" is set as the tag key
# - if there are additional ":" in the "k" value they and they are ignored and kept as part of
#   the tag key. For example:
# 
#   <tag k="addr:street:name" v="Lincoln"/>
#   should be turned into
#   {'id': 12345, 'key': 'street:name', 'value': 'Lincoln', 'type': 'addr'}
# 
# - If a node has no secondary tags then the "node_tags" field  contains an empty list.
# 
# The final return value for a "node" element looks something like:
# 
# {'node': {'id': 757860928,
#           'user': 'uboot',
#           'uid': 26299,
#        'version': '2',
#           'lat': 41.9747374,
#           'lon': -87.6920102,
#           'timestamp': '2010-07-22T16:16:51Z',
#       'changeset': 5288876},
#  'node_tags': [{'id': 757860928,
#                 'key': 'amenity',
#                 'value': 'fast_food',
#                 'type': 'regular'},
#                {'id': 757860928,
#                 'key': 'cuisine',
#                 'value': 'sausage',
#                 'type': 'regular'},
#                {'id': 757860928,
#                 'key': 'name',
#                 'value': "Shelly's Tasty Freeze",
#                 'type': 'regular'}]}
# 
# ### If the element top level tag is "way":
# The dictionary should have the format {"way": ..., "way_tags": ..., "way_nodes": ...}
# 
# The "way" field holds a dictionary of the following top level way attributes:
# - id
# -  user
# - uid
# - version
# - timestamp
# - changeset
# 
# All other attributes are ignored
# 
# The "way_tags" field holds a list of dictionaries, following the exact same rules as
# for "node_tags".
# 
# Additionally, the dictionary should have a field "way_nodes". "way_nodes" should hold a list of
# dictionaries, one for each nd child tag.  Each dictionary have the fields:
# - id: the top level element (way) id
# - node_id: the ref attribute value of the nd tag
# - position: the index starting at 0 of the nd tag i.e. what order the nd tag appears within
#             the way element
# 
# The final return value for a "way" element looks something like:
# 
# {'way': {'id': 209809850,
#          'user': 'chicago-buildings',
#          'uid': 674454,
#          'version': '1',
#          'timestamp': '2013-03-13T15:58:04Z',
#          'changeset': 15353317},
#  'way_nodes': [{'id': 209809850, 'node_id': 2199822281, 'position': 0},
#                {'id': 209809850, 'node_id': 2199822390, 'position': 1},
#                {'id': 209809850, 'node_id': 2199822392, 'position': 2},
#                {'id': 209809850, 'node_id': 2199822369, 'position': 3},
#                {'id': 209809850, 'node_id': 2199822370, 'position': 4},
#                {'id': 209809850, 'node_id': 2199822284, 'position': 5},
#                {'id': 209809850, 'node_id': 2199822281, 'position': 6}],
#  'way_tags': [{'id': 209809850,
#                'key': 'housenumber',
#                'type': 'addr',
#                'value': '1412'},
#               {'id': 209809850,
#                'key': 'street',
#                'type': 'addr',
#                'value': 'West Lexington St.'},
#               {'id': 209809850,
#                'key': 'street:name',
#                'type': 'addr',
#                'value': 'Lexington'},
#               {'id': '209809850',
#                'key': 'street:prefix',
#                'type': 'addr',
#                'value': 'West'},
#               {'id': 209809850,
#                'key': 'street:type',
#                'type': 'addr',
#                'value': 'Street'},
#               {'id': 209809850,
#                'key': 'building',
#                'type': 'regular',
#                'value': 'yes'},
#               {'id': 209809850,
#                'key': 'levels',
#                'type': 'building',
#                'value': '1'},
#               {'id': 209809850,
#                'key': 'building_id',
#                'type': 'chicago',
#                'value': '366409'}]}
# """
# 
#==============================================================================
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import audit_name_postcode
import lang
import cerberus
import schema

OSM_PATH = "mumbai.osm"


NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

        
   


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Cleans and shapes node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # To handle secondary tags of both node and way elements
    
   
    if element.tag == 'node':
        for node_attr in node_attr_fields:
            node_attribs[node_attr] = element.attrib[node_attr]
            
        tags = node_way_tags(element)
        
        
        return {'node': node_attribs, 'node_tags': tags}
        
    elif element.tag == 'way':
        for way_attr in way_attr_fields:
            way_attribs[way_attr] = element.attrib[way_attr]
         
        position = 0    
        for child in element:
            if child.tag == 'nd':
                node_dict = {}
                node_dict = {"id": element.attrib['id'],"node_id": child.attrib['ref'],"position": position}
                way_nodes.append(node_dict)
            position += 1
            
            
        tags = node_way_tags(element)
        
    return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def node_way_tags(element):
    tags = []
    for child in element:
        if child.tag == 'tag'and PROBLEMCHARS.match(child.attrib['k']) == None:
            lang.keyname(child) # converting 2-letter language code into 
                                # 3-letter language code
            
            
            
            if audit_name_postcode.is_postcode(child):       #auditing postcode
                audit_name_postcode.audit_postcode(child)
        
            if audit_name_postcode.is_street_name(child):#auditing street names
                child.attrib['v'] = audit_name_postcode.update_name(child.attrib['v'],
                                                        audit_name_postcode.mapping)
                
                
            
            key_val = child.attrib['k']
            
            if ':' in child.attrib['k']:
                
                kv = key_val.split(':',1)
                #creating tag dictionary
                tag_dict = {"id": element.attrib['id'],
                            "value": child.attrib['v'],
                            "key": kv[1],
                            "type": kv[0]}
                tags.append(tag_dict)
            if not ':' in child.attrib['k']:
                 #creating tag dictionary
                tag_dict = {"id": element.attrib['id'],
                            "value": child.attrib['v'],
                            "key": child.attrib['k'],
                            "type":'regular'}
                tags.append(tag_dict)
            
            
    
    return tags # list of tag dictionary 
    
    
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()



def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
         
        raise Exception(message_string.format(field, error_string))
 


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""
 
    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })
 
    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
 


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'wb') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'wb') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'wb') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'wb') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'wb') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)
    #get_element(OSM_PATH, tags=('node', 'way', 'relation'))

