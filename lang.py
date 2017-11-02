# -*- coding: utf-8 -*-
"""
Created on Sat Jul 29 18:04:07 2017

@author: Raman Raj
"""
import xml.etree.cElementTree as ET
SAMPLE_FILE = "mumbai.osm"

# 'code_mapping' is a dictionary where key refer to 2-letter code and value refer to 3-letter code.

code_mapping = {'bn' : 'ben',
                'cs' : 'cze',
                'en' : 'eng',
                'de' : 'ger',
                'gu' : 'guj',
                'hi' : 'hin',
                'eo' : 'epo',
                'es' : 'spa',
                'fr' : 'fre',
                'ia' : 'ina',
                'io' : 'ido',
                'ja' : 'jpn',
                'kn' : 'kan',
                'lt' : 'lit',
                'ml' : 'mal',
                'mr' : 'mar',
                'pl' : 'pol',
                'ru' : 'rus',
                'sk' : 'slo',
                'sr' : 'srp',
                'ta' : 'tam',
                'te' : 'tel',
                'uk' : 'ukr',
                'zh' : 'zha',
                'jbo': 'jbo',
                'ar' : 'ara',
                'ur' : 'urd',
                'ma' : 'ma',
                'ko' : 'kor',
                'pt' : 'por',
                'cy' : 'cym',
                'fa' : 'per',
                'gl' : 'glg',
                'he' : 'heb',
                'pa' : 'pan',
                'sv' : 'swe'}

# This list contains all the key attribute that is to be cleaned
language = []                                   
def keyname(element):
    if 'name:' in element.attrib['k']:    # These key value contains ":" 
                                          # example --> name:en
        language.append(element.attrib['k'])
        key_val = element.attrib['k']
        if key_val in language:         
            a = key_val.split(':')       # split the key attribute to extract
                                         # language part
                                         
                                         
            if code_mapping[a[1]]:      # if language code present in the dict.
            
                element.attrib['k'] = a[0]+':'+code_mapping[a[1]] #new key-attr
                return element.attrib['k']

def test():
    for event, element in ET.iterparse(SAMPLE_FILE):
        if element.tag == 'tag':
            keyname(element)    

if __name__ == '__main__':
    test()