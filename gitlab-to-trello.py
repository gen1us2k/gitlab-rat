import requests
import datetime


def info():
    user_name = input('Введите имя пользователя на gitlab.com: ')  # Имя Пользователя на gitlab.com
    get_user_id = 'https://gitlab.com/api/v4/users?username={0}'.format(user_name)
    r = requests.get(get_user_id)
    user_id = r.json()[0]['id']

    gitlab_url = 'https://gitlab.com/api/v4/users/{0}/events'.format(user_id)  # URL на события
    r = requests.get(gitlab_url).json()

    date_list = []
    for current_date in r:
        current_date = current_date['created_at']
        date = current_date.rsplit('T', 1)[0]
        date_list.append(date)

    now_date = datetime.date.today()
    start = now_date - datetime.timedelta(days=1)
    delta = datetime.timedelta(days=7)
    end = start - delta

    week_list = []
    while end < start:
        end = end + datetime.timedelta(days=1)
        date = end
        date = str(date)
        week_list.append(date)

    daily_commits = []
    for current_date in week_list:
        commit = date_list.count(current_date)
        if commit:
            info = ['за', current_date, 'коммитов было-', commit]
            daily_commits.append(info)
        else:
            info = ['за', current_date, 'коммитов не было']
            daily_commits.append(info)
    return daily_commits

info = info()

def send(info):
    id_card = input('Введите id карточки на trello.com: ')  # ID Нашей карточки в trello.com. Пример 59ae5dfc529cc2277f6a75bd или la8gztsN
    url = ("https://api.trello.com/1/cards/{0}/actions/comments").format(id_card)  # URL на добавления комментария в карточку

    text = info
    key = '433edb45fe4cb614c1124eee5733156a'  # Наш ключ в trello.com
    token = '2f01994a775cb341ff07d7f4901d5c445b2e686a2da3ec086efaf52b8f8d9ee4'  # Наш токен в trello.com

    querystring = {
        'text': text,
        'key': key,
        'token': token
    }

    response = requests.request("POST", url, params=querystring)  # Запрос на добавления комментария в карточку
    return response

send(info)