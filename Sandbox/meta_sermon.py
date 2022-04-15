import json
import requests
import sys
import xmltodict


# Variables
# sermon dictionary - used to upload data to squarespace
sermon_dict = {}

# error log dictionary
error_log = {}

# count how many entries add to tsermon dictionary
counter = 0

# count total mp3 files and bites size
file_count = 0
file_size = 0

# count
audio_counter = 0


# load the json file with the sermon data from XML emmanuel website
data = json.load(open('meta_sermon.json'))
data = data['group'][0]['group']


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
    try:
        r = requests.get(url, allow_redirects=True)
        file_name = item_id + '.mp3'
        open(file_name, 'wb').write(r.content)
    except:
        num = get_next_error_counter()
        error_log[num] = {item_id: "could not download and save file"}


# Actions
for x in range(len(data)):
    data_x = data[x]['item']

    for y in range(len(data_x)):
        data_xy = data_x[y]

        # create the dictionay entry
        sermon_dict[counter] = {
            "_id": str_exists('_item_id', data_xy, data_xy['_item_id']),
            "_title": str_exists('_title',data_xy, data_xy['_item_id']),
            "_description": str_exists('_description',data_xy, data_xy['_item_id']),
            "_author": str_exists('_author',data_xy, data_xy['_item_id']),
            "_date_time": str_exists('_recording_dt',data_xy, data_xy['_item_id']), 
            "_bible_ref": str_exists('_bible_book',data_xy, data_xy['_item_id']) + str_exists('_bible_chapter', data_xy, data_xy['_item_id']),
            "_keywords": str_exists('_keywords', data_xy, data_xy['_item_id']),
            "_web_url": str_exists('_url',data_xy['link'], data_xy['_item_id']),
            "_file_name": str_exists('_item_id', data_xy, data_xy['_item_id']) + ".mp3"
        }

        # download the file and remane
        url = str_exists('_file_base_path',data_xy['file'][0], data_xy['_item_id']) + str_exists('_file_name',data_xy['file'][0], data_xy['_item_id'])
        item_id = str_exists('_item_id', data_xy, data_xy['_item_id'])
        if audio_counter <= 4:
            get_sermon_audio(url, item_id)
            audio_counter = audio_counter + 1


        counter = counter + 1


for x in range(len(data)):
    data_x = data[x]['item']

    for y in range(len(data_x)):
        data_xy = data_x[y]
        new_file_size = int_exists('_file_size',data_x[y]['file'][0], data_xy['_item_id'])
        file_size = file_size + new_file_size
        if new_file_size > 0:
            file_count = file_count + 1


print("Total size of all files is {} MB".format(round(file_size / 1048576,)))
print("Total size of all files is {} GB".format(round(file_size / 1073741824)))
print("from {} files".format(file_count))

report_error_log()