

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "chennai_india.osm"

regex = re.compile(r'\b\S+\.?$', re.IGNORECASE)
postcode_re = re.compile(r'[-a-zA-Z=:\+/&<>;\'"\?%#$@\,\. \t\r\n]')


expected = ["Street", "Avenue", "Court", "Place", "Square", "Lane", "Road", "Nagar", "Chennai",
            "tulasinga"] #expected names in the dataset

mapping = { "Ave":"Avenue",
            "St.": "Street",
            "Rd." : "Road",
            "N.":"North",
            "St" : "Street",
            "St." : "Street",
            "no" : "No",
            "Rd." : "Road",
            "Rd" : "Road",
            "ROAD" : "Road",
            "ROad" : "Road",
            "st" : "Street",
            "road" : "Road",
            "stn" : "Station",
            "strret" : "Street",
            "slai" : "Salai",
            "nagar" : "Nagar",
            }

# Search string for the regex. If it is matched and not in the expected list then add this as a key to the set.
def audit_street(street_types, street_name): 
    m = regex.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem): # Check if it is a street name
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile): # return the list that satify the above two functions
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street(street_types, tag.attrib['v'])
    osm_file.close()

    return street_types

#pprint.pprint(dict(audit(OSMFILE))) # print the existing names

def string_case(s): # change string into titleCase except for UpperCase
    if s.isupper():
        return s
    else:
        return s.title()

# return the updated names
def update_name(name):
    after = []
    # Split name string to test each part individually
    for part in name.split(" "):
        # remove any extra characters in string and make all lower-case
        part = part.strip(",_\.-").lower()
        # Check each part of the name against the keys in the correction dict        
        if part in mapping.keys():
            # If is a key in the dictionary then overwrite that part of the name with the dictionary value for it
            part = mapping[part]
        # Reassemble and capitalize first letter    
        after.append(part.capitalize())
    # Return all pieces of the name as a string joined by a space.
    return " ".join(after)

update_street = audit(OSMFILE) 
#pprint.pprint(dict(update_street))
######################################
#POSTCODE - AUDIT
######################################

#Determine if this is this an address
def is_address(elem):
    if elem.attrib['k'][:5] == "addr:":
        return True

#Determine if a tag contains a postcode
def is_postcode(elem):
    return (elem.attrib['k'] == "addr:postcode")

#Find all unique postal codes
data_block=[]
osm_file = open(OSMFILE, "r")
for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postcode(tag):
                    data_block.append(tag.attrib['v'])
                    
osm_file.close()

#pprint.pprint(data_block)

def audit_postcode_value(postcode):
    m = postcode_re.search(postcode)
    global postcode_value
    if m:
        postcode_value=postcode
    if len(postcode)<=6:
        postcode_value=postcode
        postcode_value=postcode
    
    return postcode_value


def audit_postcode(osmfile):
    osm_file = open(osmfile, "r")
    #postcode_values = collections.defaultdict(set)
    postcode_values=[]
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postcode(tag):
                    #audit_postcode_value(postcode_values, tag.attrib['v'])
                    postcode_values.append(audit_postcode_value(tag.attrib['v']))
    osm_file.close()
    return postcode_values

def clean_postcode(postcode):
    if len(postcode)<=6:
        new_postcode=int(postcode.strip()[:6])
    else:
        new_postcode=int(postcode.strip())
    return new_postcode

#pprint.pprint(audit_postcode(OSMFILE))

audit_postcode(OSMFILE)

#pprint.pprint(dict(audit_postcode(OSMFILE)))
# print the updated names
for street_type, ways in update_street.iteritems():
    for name in ways:
        better_name = update_name(name)
#print name, "=>", better_name

