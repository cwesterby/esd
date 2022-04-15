
import requests

url = "https://s3.us-east-1.amazonaws.com/media.1683.churchinsight.com/f45c384b-e4c9-4011-b1a3-b66e665cf74b.mp3"

r = requests.get(url, allow_redirects=True)

print(r.headers.get('content-type'))

# open('test.mp3', 'wb').write(r.content)



# <a class="media-file-download media-file-control"