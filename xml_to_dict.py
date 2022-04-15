import xmltodict
import json

with open('feed.xml') as xml_file:
    my_dict=xmltodict.parse(xml_file.read())

xml_file.close()
json_data=json.dumps(my_dict)
print(json_data)

