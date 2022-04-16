import json
import requests
import sys
import xmltodict
import pprint

# Variables
# xml url and file name to save 
url = 'https://www.emmanuelwimbledon.org.uk/Media/MediaXML.xml?fid=2775'
xml_file_name = 'output/feed.xml'

# sermon dictionary - used to upload data to squarespace
sermon_dict = {}

# error log dictionary
error_log = {}

# count how many entries add to tsermon dictionary
counter = 0

# count total mp3 files and bites size
file_count = 0
file_size = 0

# count for audio
audio_counter = 0


# Functions
# get the xml url feed and save xml file
def get_sermon_xml(url,xml_file_name):
    try:
        f = open(xml_file_name)
        print("XML file already exists")
    except FileNotFoundError:
        response = requests.get(url)
        with open(xml_file_name, 'wb') as file:
            file.write(response.content)
        print("xml file created")

# open xml file and json to dictionary
def convert_xml_Json(xml_file_name):
    with open(xml_file_name) as xml_file:
        my_dict=xmltodict.parse(xml_file.read())
    xml_file.close()
    return my_dict


# Functions
# checks if key is in the dictionary - string output
def str_exists(val, dict, item_id):
    if val in dict:
        return dict[val]
    else:
        num = get_next_error_counter()
        error_log[num] = {item_id: "could not find {}".format(val)}
        return ""
        # print("can not find for {}".format(dict['_item_id']))

# checks if key is in the dictionary - int output
def int_exists(val, dict, item_id):
    if val in dict:
        return int(dict[val])
    else:
        num = get_next_error_counter()
        error_log[num] = {item_id: "could not find {}".format(val)}
        return 0
        # print("can not find for {}".format(dict['_item_id']))

# increments the error counter
def get_next_error_counter():
    return len(error_log) + 1

# prints out all errors captured to console line by line
def report_error_log():
    for x in error_log:
        print(x , error_log[x])


# download the file and remane
def get_sermon_audio(url, item_id):
    file_name = 'media/' + item_id + '.mp3'
    try:
        f = open(xml_file_name)
        print("media file already exists")
    except:
        try:
            r = requests.get(url, allow_redirects=True)
            open(file_name, 'wb').write(r.content)
        except:
            num = get_next_error_counter()
            error_log[num] = {item_id: "could not download and save file"}


def add_sermon_entry(sermon_dict, counter, data):
    sermon_dict[counter] = {
        "@id": str_exists('@item_id', data, data['@item_id']),
        "@title": str_exists('@title',data, data['@item_id']),
        "@description": str_exists('@description',data, data['@item_id']),
        "@author": str_exists('@author',data, data['@item_id']),
        "@date_time": str_exists('@recording_dt',data, data['@item_id']), 
        "@bible_ref": str_exists('@bible_book',data, data['@item_id']) + " " + str_exists('@bible_chapter', data, data['@item_id']),
        "@keywords": str_exists('@keywords', data, data['@item_id']),
        "@web_url": str_exists('@url',data['link'], data['@item_id']),
        "@file_name": str_exists('@item_id', data, data['@item_id']) + ".mp3"
    }

    url = str_exists('@file_base_path',data['file'], data['@item_id']) + str_exists('@file_name',data['file'], data['@item_id'])
    item_id = str_exists('@item_id', data, data['@item_id'])
    print("sermon entry " + item_id + "complete, now starting audio")
    get_sermon_audio(url, item_id)


def saving_file(filename, data):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)
    print(filename + " saved")


# ACTIONS
# load the json file with the sermon data from XML emmanuel website
get_sermon_xml(url,xml_file_name)
json_data = convert_xml_Json(xml_file_name)

data0 = json_data['media']['group']['item']
data1 = json_data['media']['group']['group']



## tree 
# ['media']['group']['item'] = 30
for x in range(len(data0)):
    data_x = data0[x]
    # create the dictionay entry
    # download the file and remane
    add_sermon_entry(sermon_dict, counter, data_x)
    counter = counter + 1


# ['media']['group']['group'] = 9
for x in range(len(data1)):
    data_x = data1[x]['item']

    for y in range(len(data_x)):
        data_xy = data_x[y]

        # create the dictionay entry
        # download the file and remane
        add_sermon_entry(sermon_dict, counter, data_xy)
        counter = counter + 1


# # this section is for the file size
# for x in range(len(data)):
#     data_x = data[x]['item']

#     for y in range(len(data_x)):
#         data_xy = data_x[y]
#         new_file_size = int_exists('@file_size',data_x[y]['file'], data_xy['@item_id'])
#         file_size = file_size + new_file_size
#         if new_file_size > 0:
#             file_count = file_count + 1


# print("Total size of all files is {} MB".format(round(file_size / 1048576,)))
# print("Total size of all files is {} GB".format(round(file_size / 1073741824)))
# print("from {} files".format(file_count))

saving_file("output/sermons.json", sermon_dict)
saving_file("output/errors.json", error_log)
