#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import requests

from datetime import datetime, timedelta
from optparse import OptionParser


DAY_OFFS = (0, 6)


def get_commits_status_for_user(username, token):
    print("Grabbing user info for {} username".format(username))
    resp = requests.get("https://gitlab.com/api/v4/users?username={}".format(username))
    user_id = resp.json()[0].get('id', 0)
    if user_id == 0:
        return "user {} not found".format(username)

    print("Grabbing events data...")
    params = {
        "private_token": token,
        "before": datetime.now().strftime("%Y-%m-%d"),
        "after": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
    }
    r = requests.get("https://gitlab.com/api/v4/users/{}/events".format(user_id), params=params)
    messages = []
    for i in xrange(7):
        day = datetime.now() - timedelta(i)
        commits = 0
        for event in r.json():
            commit_date = datetime.strptime(event.get("created_at"), "%Y-%m-%dT%H:%M:%S.%fZ")
            if (day - commit_date).days == 0:
                commits += 1

        if (datetime.now() - day).days == 0 and commits == 0:
            continue

        if commits == 0 and day.weekday() not in DAY_OFFS:
            messages.append("No commits for {}".format(day.strftime("%Y-%m-%d")))

        if commits > 0 and day.weekday() in DAY_OFFS:
            messages.append("There are {} commits on day off of {}".format(commits, day.strftime("%Y-%m-%d")))

    return "\n".join(messages)


def send_to_trello(key, token, card_id, message):
    data = {
        "text": message,
        "key": key,
        "token": token,
    }
    r = requests.post("https://api.trello.com/1/cards/{}/actions/comments".format(card_id), data=data)
    return r.content


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-u", "--username", dest="username", help="Gitlab username for user to check to")
    parser.add_option("-t", "--trello-card-id", dest="trello_id", help="Trello card ID to leave comment")
    parser.add_option("--gitlab_token", dest="gitlab_token", help="Gitlab private token")
    parser.add_option("--trello_key", dest="trello_key", help="Gitlab private token")
    parser.add_option("--trello_token", dest="trello_token", help="Gitlab private token")

    (options, args) = parser.parse_args()
    if not options.username or not options.trello_id or not options.gitlab_token:
        parser.print_help()
        sys.exit(0)

    status_message = get_commits_status_for_user(options.username, options.gitlab_token)
    print send_to_trello(options.trello_key, options.trello_token, options.trello_id, status_message)
