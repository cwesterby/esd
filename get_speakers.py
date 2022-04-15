import json

with open('sermons.json') as json_file:
  data = json.load(json_file)


speakers = {}


for x in data:
    if data[x]['@author'] in speakers:
        speakers[data[x]['@author']] += 1
    else:
        speakers[data[x]['@author']] = 1


print(speakers)
