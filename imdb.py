from PIL import Image
import requests
from io import BytesIO
import re
from bs4 import BeautifulSoup
import os
import io

class imdb:


    def __init__(self, name):

        '''
        parse html to return the movie title and year associated with a given entry:
        '''
        base_url = "https://www.imdb.com/title/"
        self.name = name
        self.url = base_url + self.name + "/"

    def title(record):
        url = requests.get(record.url)
        data = url.text
        soup = BeautifulSoup(data, 'lxml')
        tags = soup.find_all('h1')
        for tag in tags:
            text = tag.text
        return text.replace(u'\xa0', u' ')

    def image_index_urls(record):
        '''
        return list of urls with image files for a given record:
        '''
        url = requests.get(record.url + "mediaindex")
        data = url.text
        soup = BeautifulSoup(data, 'lxml')

        #find all 'a' tags with an href attribute, then append those tags
        tags = soup.find_all('a')
        href_list = [record.url + "mediaindex"]
        for tag in tags:
            if "page=" in str(tag.get('href')):
                href_list.append("https://www.imdb.com" + tag.get('href'))
        return set(href_list)#.add(record.url + "mediaindex")

    def all_image_urls(record):
        '''
        return list of all associated images for a given record:
        '''
        href_list = record.image_index_urls()
        image_url_list = []
        for url in href_list:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            img_tags = soup.find_all('img')
            for img in img_tags:
                if img['src'][-3:] == "jpg":
                    image_url_list.append(img['src'])
            #images = [img['src'] for img in img_tags if img['src'][-3:] == "jpg"]
            #image_list.append(images)
        return image_url_list

    def retrieve_jpgs(record):
        '''
        generate a list of all jpgs associated with a record:
        '''
        image_url_list = record.all_image_urls()

        jpg_list = []
        for img in image_url_list:
            img_response = requests.get(img)
            jpg_list.append(Image.open(BytesIO(img_response.content)))
        return jpg_list


    def save_pngs(record):
        '''
        save all images associated with a record locally, as pngs:
        '''

        image_url_list = record.all_image_urls()

        if not os.path.exists(str(record.name) + "_images"):
            os.mkdir(str(record.name) + "_images")
        else:
            print('directory already exists')

        for i, img in enumerate(image_url_list):
            img_response = requests.get(img)
            jpg = Image.open(BytesIO(img_response.content))
            file_name = str(record.name) + "_image_" + str(i)
            #jpg.save("record/" + str(file_name), "PNG")
            jpg.save(str(record.name) + "_images/" + str(file_name), "PNG")
