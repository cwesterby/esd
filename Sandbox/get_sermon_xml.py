import requests

url = 'https://www.emmanuelwimbledon.org.uk/Media/MediaXML.xml?fid=2775'
xml_file_name = 'feed.xml'

def get_sermon_xml(url,xml_file_name):
    try:
        f = open(xml_file_name)
        print("File already exists")
    except FileNotFoundError:
        response = requests.get(url)
        with open(xml_file_name, 'wb') as file:
            file.write(response.content)
        print("xml file created")


get_sermon_xml(url,xml_file_name)
