#!/usr/bin/env python
from six.moves import range
import urllib
import string
import random

import requests


BASE_URL = 'https://club.pokemon.com/us/pokemon-trainer-club'
DUPE_EMAIL_DEST = 'https://club.pokemon.com/us/pokemon-trainer-club/forgot-password?msg=users.email.exists'
DUPE_NAME_DEST = 'https://club.pokemon.com/us/pokemon-trainer-club/parents/sign-up'
SUCCESS_DEST = 'https://club.pokemon.com/us/pokemon-trainer-club/parents/email'


def print_headers(headers):
    for head, value in sorted(headers.iteritems()):
        print('  {}: {}'.format(head, value))


def random_string(length=10):
    return ''.join(
        [random.choice(string.ascii_letters + string.digits) for _ in range(length)]
    )


class MySession(requests.Session):

    def request(self, method, url, headers={}, data=None, **kwargs):
        if isinstance(data, dict):
            data = urllib.urlencode(data, doseq=True)
        req = requests.Request(method, url, data=data, **kwargs)
        prepped = self.prepare_request(req)
        prepped.headers.update(headers)
        return self.send(prepped)


def main():
    s = MySession()

    username = random_string()
    password = random_string()
    email = '{}@{}.com'.format(random_string(), random_string(4))

    resp = s.request(
        'GET',
        '{base_url}/parents/sign-up'.format(base_url=BASE_URL),
        headers={
            # 'Host': 'club.pokemon.com',
            # 'Connection': 'keep-alive',
            # 'Upgrade-Insecure-Requests': '1',
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            # 'Accept-Encoding': 'gzip, deflate, sdch, br',
            # 'Accept-Language': 'en-US,en;q=0.8',
        }
    )

    resp = s.request(
        'POST',
        '{base_url}/sign-up/'.format(base_url=BASE_URL),
        headers={
            # 'Host': 'club.pokemon.com',
            # 'Cache-Control': 'max-age=0',
            # 'Origin': 'https://club.pokemon.com',
            # 'Upgrade-Insecure-Requests': '1',
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': '{base_url}/sign-up/'.format(base_url=BASE_URL),
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Accept-Language': 'en-US,en;q=0.8'
        },
        data={
            'csrfmiddlewaretoken': s.cookies.get_dict()['csrftoken'],
            'dob': '1970-01-01',
            'country': 'US',
        }
    )

    resp = s.request(
        'POST',
        '{base_url}/parents/sign-up'.format(base_url=BASE_URL),
        headers={
            # 'Host': 'club.pokemon.com',
            # 'Cache-Control': 'max-age=0',
            # 'Origin': 'https://club.pokemon.com',
            # 'Upgrade-Insecure-Requests': '1',
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': '{base_url}/parents/sign-up'.format(base_url=BASE_URL),
            # 'Accept-Encoding': 'gzip, deflate, br',
            # 'Accept-Language': 'en-US,en;q=0.8'
        },
        data={
            'csrfmiddlewaretoken': s.cookies.get_dict()['csrftoken'],
            'username': username,
            'password': password,
            'confirm_password': password,
            'email': email,
            'confirm_email': email,
            'public_profile_opt_in': 'False',
            'screen_name': '',
            'terms': 'on',
        }
    )

    print(resp.status_code)

    print('Headers:')
    print_headers(resp.headers)
    # print(resp.text.encode('utf8'))

    print('Final Url:')
    print(resp.url)

    # # Dump the return text to an html file for visual inspection
    # with open('test.html', 'w') as f:
    #     f.write(resp.text.encode('utf-8'))

    if resp.url == SUCCESS_DEST:
        print('User successfully created!  Username: {}, Password: {}'.format(username, password))
        return
    elif resp.url == DUPE_EMAIL_DEST:
        print('User creation failed!  Email already in use.')
    elif resp.url == DUPE_NAME_DEST:
        print('User creation failed!  Username "{}" already in use.'.format(username))
    else:
        print('Generic failure. User was not created.')

    return


if __name__ == '__main__':
    main()
