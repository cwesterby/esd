import json
import requests
import xmltodict
from datetime import datetime
import shutil
import os.path

# Variables
url = 'https://www.emmanuelwimbledon.org.uk/Media/MediaXML.xml?fid=2775'
today = datetime.today().strftime('%Y-%m-%d')
counter = 0
error_log = {}
counter = 0
file_count = 0
file_size = 0
old_json = {}

# FILE NAMES
xml_file_name = 'feed'+today+'.xml'
error_file_name = 'error'+today+'.json'
json_file_name = 'sermon'+today+'.json'

# PATHS
path_archive = 'archive/'
path_output = 'output/'
path_media = 'media/'

#FILES
xml_file = path_output + xml_file_name
error_file = path_output + error_file_name
json_file = path_output + json_file_name


# FUNCTIONS
# get the xml url feed and save xml file
def get_sermon_xml(url,file):
    try:
        f = open(file)
        print('XML file already exists. Moving '+ file +' file to archive')
        shutil.move(file, path_archive+xml_file_name)
        response = requests.get(url)
        with open(file, 'wb') as file:
            file.write(response.content)
        print("New xml file created")

    except FileNotFoundError:
        response = requests.get(url)
        with open(file, 'wb') as file:
            file.write(response.content)
        print("xml file created")

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

# open xml file and json to dictionary
def convert_xml_Json(file):
    with open(file) as xml_file:
        my_dict=xmltodict.parse(xml_file.read())
    xml_file.close()
    return my_dict

def add_sermon_entry(sermon_dict, counter, data):
    sermon_dict[counter] = {
        "@id": str_exists('@item_id', data, data['@item_id']),
        "@title": str_exists('@title',data, data['@item_id']),
        "@description": str_exists('@description',data, data['@item_id']),
        "@author": str_exists('@author',data, data['@item_id']),
        "@date_time": str_exists('@recording_dt',data, data['@item_id']), 
        "@bible_ref": str_exists('@bible_book',data, data['@item_id']) + " " + str_exists('@bible_chapter', data, data['@item_id']),
        "@keywords": str_exists('@keywords', data, data['@item_id']),
        "@file_name": str_exists('@item_id', data, data['@item_id']) + ".mp3",
        "@download_locaton":str_exists('@file_base_path',data['file'],data['@item_id'])  + str_exists('@file_name',data['file'],data['@item_id'])
    }

    url = str_exists('@file_base_path',data['file'], data['@item_id']) + str_exists('@file_name',data['file'], data['@item_id'])
    item_id = str_exists('@item_id', data, data['@item_id'])


# restructure the sermons 
def restrucutre_sermons(json_data, counter):
    sermon_dict = {}

    data0 = json_data['media']['group']['item']
    data1 = json_data['media']['group']['group']

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
    
    return sermon_dict

def get_sermon_json(file):
    data = {}
    try:
        with open(file) as json_file:
            data = json.load(json_file)
    except:
        date = {}
    return data

def saving_file(filename, data):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)
    print(filename + " saved")



def sermon_download(file):
    j_file = get_sermon_json(file)
    for x in j_file:
        file_exists = os.path.exists('media/' + j_file[x]['@file_name'])
        # print(j_file[x]['@download_locaton'])
        # print(file_exists)
        if file_exists == False:
            try:
                r = requests.get(j_file[x]['@download_locaton'], allow_redirects=True)
                open('media/' + j_file[x]['@file_name'], 'wb').write(r.content)
                print('saved '+ j_file[x]['@file_name'])
            except:
                print('unable to downlaod file' + j_file[x]['@file_name'])

        

if __name__ == "__main__":
    get_sermon_xml(url,xml_file)
    json_data = convert_xml_Json(xml_file)
    new_json = restrucutre_sermons(json_data, counter)
    old_json = get_sermon_json('output/sermons.json')

    if len(old_json) != len(new_json):
        # do nothing
        print("nothing has changed")
    else:
        print("Update required. Archiving ")
        shutil.move("output/sermons.json", "archive/sermons.json")
        shutil.move("output/errors.json", "archive/errors.json")

        saving_file("output/sermons.json", new_json)
        saving_file("output/errors.json", error_log)
    
    sermon_download('output/sermons.json')

