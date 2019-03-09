from requests import get, post
print(get('http://localhost:5000/api/users/1').json())
user = {
    'username': 'user4',
    'channel_name': 'user4_channel',
    'email': 'user3@mail.com',
    'birthday': '01.01.2003',
    'interests': 'программирование, Python, философия',
    'about_channel': 'Канал обо всем на свете для пользователя user3',
    'meta_tags': 'программирование, Python, философия',
    'password': 'user4',
}
print(post('http://localhost:5000/api/users', json=user).json())