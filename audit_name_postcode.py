# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 21:10:35 2017

@author: Ekta Raj
"""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

SAMPLE_FILE = "sample_file.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
regular_ex = re.compile("400\d{3}")

expected = ["Street", "Lane", "Road", "Nagar","Marg", "Colony", "Society", "Residency", "Building"]


mapping = { "Soc.": "Society",
            "Rd":"Road",
            "Coloney":"Colony",
            "bld.":"Building"
            }


def audit_street_type(street_types, street_name):
     '''This function is taken from case study'''
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
            
def audit_postcode(tag):          
    '''This function validates the postcode by matching with
    the regular expression or updating with the correct form'''
    if regular_ex.match(tag.attrib['v']): #matching with the regular expression
        return tag.attrib['v']
    else:
        tag.attrib['v'] = update_postcode(tag.attrib['v'])#call update_postcode
        return tag.attrib['v']                   #returns corrected postode
            
                                   


def is_street_name(elem):
     '''This function is taken from case study'''
    if elem.attrib['k'] == "addr:street" or elem.attrib['k']== "name":
        return True
    else:
        return False
    
    
def is_postcode(tag):
    '''This function finds the key attribute which is to be considered
    for auditing postcodes.'''
    if tag.attrib['k'] =='addr:postcode':
        return True
    else:
        return False


    
def audit(osmfile):
     '''This function is taken from case study'''
    osm_file = open(SAMPLE_FILE, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
                if is_postcode(tag):
                   audit_postcode(tag)
                
    osm_file.close()
    return street_types


def update_name(name, mapping):
    '''This function is taken from case study'''
    m = street_type_re.search(name)
    if m:
        if m.group() not in expected:
            if m.group() in mapping.keys():
                name = re.sub(m.group(), mapping[m.group()], name)
    return name

def update_postcode(tag):
    '''This function does the real task of correcting the incorrect postcodes'''
    if tag == '40049':                #replace with correct postcode
        return '400049'
    elif tag == '4000072':
        return '400072'
    elif tag == '40058':
        return '400058'
    elif tag == '40076':
        return '400076'
    elif tag == '40001':
        return '400001'
    elif tag == '123':
        return '400089' 
    elif tag == '48147':
        return '400054'
    
    else: 
        return tag.replace(" ","")    #replace the whitespace with empty string
            

def test():
    st_types = audit(SAMPLE_FILE)
   
    #pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            return update_name(name, mapping)

                
    


if __name__ == '__main__':
    test()