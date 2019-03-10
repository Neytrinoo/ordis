from requests import get, post, delete, put

# print(get('http://localhost:5000/api/users/1').json())
user = {
    'username': 'user10',
    'channel_name': 'user10_channel',
    'email': 'user10@mail.com',
    'birthday': '11.02.1991',
    'interests': 'программирование, Python, философия, биология',
    'about_channel': 'Канал обо всем на свете для пользователя user5',
    'meta_tags': 'программирование, Python, философия',
    'password': 'user10',
}
# print(get('http://localhost:5000/api/users/1').json())
user_put = {
    'username': 'user10',
    'channel_name': 'мой канал',
    'interests': 'химия, физика',
    'about_channel': 'Канал обо всем на свете для пользователя user5',
    'password': 'user10',
}
# print(post('http://localhost:5000/api/users', json=user).json())
# print(delete('http://localhost:5000/api/users/4', json={'username': 'user4', 'password': 'user4'}).json())
# print(put('http://localhost:5000/api/users/7', json=user_put).json())
# print(get('http://localhost:5000/api/users').json())
# print(get('http://localhost:5000/api/lessons/6').json())
# print(put('http://localhost:5000/api/lessons/6', json={'username': 'Neytrino', 'password': 'neytrino', 'about_lesson': 'Это конечно да, но нет'}).json())
# print(get('http://localhost:5000/api/lessons/1').json()['lesson']['comments'])
# print(get('http://localhost:5000/api/lessons').json()['lessons']['1']['comments'])
# print(delete('http://localhost:5000/api/lessons/7', json={'username': 'Neytrino', 'password': 'neytrino'}).json())
# print(get('http://localhost:5000/api/comments/5').json())
# print(post('http://localhost:5000/api/comments',
#            json={'username': 'Neytrino', 'password': 'neytrino', 'text': 'Урок классный, рекомендую', 'lesson_id': '1', 'rating': '10'}).json())
# print(delete('http://localhost:5000/api/comments/5', json={'username': 'Neytrino', 'password': 'neytrino'}).json())
# print(get('http://localhost:5000/api/comments/5').json())
# print(put('http://localhost:5000/api/comments/2',
#           json={'username': 'Neytrino', 'password': 'neytrino', 'text': 'Урок атлишный, еще раз вам говорю!', 'rating': '10'}).json())
