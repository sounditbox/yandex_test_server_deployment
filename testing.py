from requests import get, post, delete

# for i in range(10):
#     print(i, get(f'http://localhost:5000/api/news/{i}').json())

# print(get('http://localhost:5000/api/news/q').json())

# print(post('http://localhost:5000/api/news').json())
#
# print(post('http://127.0.0.1:5000/api/news',
#            json={'title': 'Заголовок'}).json())
#
# print(post('http://localhost:5000/api/news',
#            json={'title': 'Заголовок тестовой новости-2',
#                  'content': 'Текст новости, отосланный из testing.py',
#                  'user_id': 1,
#                  'is_private': False}).json())

# print(delete('http://localhost:5000/api/news/999').json())
# # новости с id = 999 нет в базе

# print(delete('http://localhost:5000/api/news/1'))

print(get('http://localhost:5000/api/v2/users').json())
print(get('http://localhost:5000/api/v2/users/1').json())
print(post('http://localhost:5000/api/v2/users',
           json={
            'name':'apiv2user_test',
            'about':'New user created via test on APIv2',

           }).json())
