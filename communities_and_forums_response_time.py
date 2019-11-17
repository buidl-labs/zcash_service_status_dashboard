import requests
from prometheus_client import (Enum, Gauge, Histogram, Summary,
                               start_http_server)

start_http_server(8096)


def get_response_time(url):
    try:
        return(requests.get(url).elapsed.total_seconds())
    except requests.exceptions.ConnectionError:
        return -1


def set_response_time(response_time, prometheus_gauge):
    prometheus_gauge.set(response_time)


def monitor_response_time():
    # gauge for all communities to send response time to server.
    chat_zcashcommunity_response_time = Gauge(
        'chat_zcashcommunity_response_time', 'chat_zcashcommunity_response_time_gauge', )
    forum_zcashcommunity_response_time = Gauge(
        'forum_zcashcommunity_response_time', 'forum_zcashcommunity_response_time_gauge')
    zcashcommunity_response_time = Gauge(
        'zcashcommunity_response_time', 'zcashcommunity_response_time_gauge')
    zcash_response_time = Gauge(
        'zcash_response_time', 'zcash_response_time_gauge')
    zfnd_response_time = Gauge(
        'zfnd_response_time', 'zfnd_response_time_gauge')

    # community: url, gauge mapping
    communities = {
        'chat.zcashcommunity.com': {'url': 'https://chat.zcashcommunity.com/home', 'gauge': chat_zcashcommunity_response_time},
        'forum.zcashcommunity.com': {'url': 'https://forum.zcashcommunity.com/', 'gauge': forum_zcashcommunity_response_time},
        'zcashcommunity.com': {'url': 'https://www.zcashcommunity.com/', 'gauge': zcashcommunity_response_time},
        'z.cash': {'url': 'https://z.cash/', 'gauge': zcash_response_time},
        'zfnd.org': {'url': 'https://www.zfnd.org/', 'gauge': zfnd_response_time}
    }

    for community in communities.keys():
        community_url = communities[community]['url']
        gauge = communities[community]['gauge']
        response_time = get_response_time(community_url)
        set_response_time(response_time, gauge)


counter = 1
while True:
    from time import sleep
    sleep(5)
    if counter % 1000 == 0:
        print('{} runs on response time are done.'.format(counter))
    try:
        monitor_response_time()
    except:
        pass
    counter += 1
