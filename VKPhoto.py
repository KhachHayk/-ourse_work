import requests
import os
import json
from tqdm import tqdm


with open(os.path.join(os.getcwd(), 'token.txt'), 'r') as token_file:
    token_vk = token_file.readline().strip()


def main():
    class VkDownloader_photo:

        def get_photos(self, offset=0, count=50):
            url = 'https://api.vk.com/method/photos.get'
            params = {'owner_id': user_id,
                      'album_id': 'profile',
                      'access_token': token_vk,
                      'v': '5.131',
                      'extended': '1',
                      'photo_sizes': '1',
                      'count': count,
                      'offset': offset
                      }
            res = requests.get(url=url, params=params)
            return res.json()

        def get_all_photos(self):

            """Определение количество всех фото профиля.
             Создание списка всех загруженных фото. создание словаря (Фото - URL фото с максимальным разрешением.
             Создание папки на ПК для скачивания фото. Формирование в .json. Скачиваем фото в паку на ПК"""

            data = self.get_photos()
            all_photo_count = data['response']['count']
            i = 0
            count = 50
            photos = []
            max_photo = {}

            if not os.path.exists('photo_vk'):
                os.mkdir('photo_vk')


            while i <= all_photo_count:
                if i != 0:
                    data = self.get_photos(offset=i, count=count)

                for photo in data['response']['items']:
                    max_size = 0
                    photos_info = {}
                    for size in photo['sizes']:
                        if size['height'] >= max_size:
                            max_size = size['height']
                    if photo['likes']['count'] not in max_photo:
                        max_photo[photo['likes']['count']] = size['url']
                        photos_info['file_name'] = f"{photo['likes']['count']}.jpg"
                    else:
                        max_photo[f"{photo['likes']['count']} + {photo['date']}"] = size['url']
                        photos_info['file_name'] = f"{photo['likes']['count']}+{photo['date']}.jpg"

                    photos_info['size'] = size['type']
                    photos.append(photos_info)

                for photo_name, photo_url in max_photo.items():
                    with open('photo_vk/%s' % f'{photo_name}.jpg', 'wb') as file:
                        img = requests.get(photo_url)
                        file.write(img.content)

                print(f'Загружено {len(max_photo)} фото')
                i += count

            with open("photos.json", "w") as file:
                json.dump(photos, file, indent=4)

    class YaUploader:
        def __init__(self, token: str):

            """Капирования фото на Яндекс Диск из папки на ПК"""

            self.token = token

        def create_folder(self):
            url = f'https://cloud-api.yandex.net/v1/disk/resources/'
            headers = {'Content-Type': 'application/json',
                       'Authorization': f'OAuth {ya_token}'}
            params = {'path': f'{folder_name}',
                      'overwrite': 'false'}
            response = requests.put(url=url, headers=headers, params=params)

        def upload(self, file_path: str):
            url = f'https://cloud-api.yandex.net/v1/disk/resources/upload'
            headers = {'Content-Type': 'application/json',
                       'Authorization': f'OAuth {ya_token}'}
            params = {'path': f'{folder_name}/{file_name}',
                      'overwrite': 'true'}


            response = requests.get(url=url, headers=headers, params=params)
            href = response.json().get('href')

            uploader = tqdm(requests.put(href, data=open(files_path, 'rb')))

    user_id = str(input('Введите id VK: '))
    downloader = VkDownloader_photo()
    downloader.get_all_photos()

    ya_token = str(input('Введите ваш токен ЯндексДиск: '))
    uploader = YaUploader(ya_token)
    folder_name = str(input('Введите имя папки на ЯндексДиске: '))
    uploader.create_folder()

    photos_list = os.listdir('photo_vk')
    count = 0
    for photo in photos_list:
        file_name = photo
        files_path = os.getcwd() + '\photo_vk\\' + photo
        result = uploader.upload(files_path)
        count += 1
        print(f'Фотографий загружено на ЯндексДиск: {count}')


if __name__ == '__main__':
    main()