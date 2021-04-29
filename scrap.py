import re
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup

top100_urls = [
    "/top/bestofrt/top_100_action__adventure_movies/",
    "/top/bestofrt/top_100_animation_movies/",
    "/top/bestofrt/top_100_art_house__international_movies/",
    "/top/bestofrt/top_100_classics_movies/",
    "/top/bestofrt/top_100_comedy_movies/",
    "/top/bestofrt/top_100_documentary_movies/",
    "/top/bestofrt/top_100_drama_movies/",
    "/top/bestofrt/top_100_horror_movies/",
    "/top/bestofrt/top_100_kids__family_movies/",
    "/top/bestofrt/top_100_musical__performing_arts_movies/",
    "/top/bestofrt/top_100_mystery__suspense_movies/",
    "/top/bestofrt/top_100_romance_movies/",
    "/top/bestofrt/top_100_science_fiction__fantasy_movies/",
    "/top/bestofrt/top_100_special_interest_movies/",
    "/top/bestofrt/top_100_sports__fitness_movies/",
    "/top/bestofrt/top_100_television_movies/",
    "/top/bestofrt/top_100_western_movies/",
]

base_url = "https://www.rottentomatoes.com"


def step1():
    """
    Input: top100_urls.
    
    Get url of movies from the `top100_urls`.
    """
    fd = open('step1.json', 'w')
    for top100_url in top100_urls:
        url = base_url + top100_url
        text = requests.get(url).text
        text = BeautifulSoup(text, 'html.parser').find('script', attrs={'id': 'jsonLdSchema'}).contents[0].strip()
        data = json.loads(text)
        data = data['itemListElement']
        json.dump(data, fd)
        fd.write('\n')
    fd.close()


from rotten_tomatoes_client import RottenTomatoesClient

proxies = {
    "http": "http://127.0.0.1:1081",
    "https": "http://127.0.0.1:1081",
}


def step2():
    """
    Input: step1.json
    
    1. Extract urls and visit every url
    2. Find the movieId of each movie
    3. Use `rotten_tomatoes_client` and get the detail of movie
    4. Store the information into json
      
    """
    cnt = 0
    start = 0
    with open('step1.json') as fd:
        while True:
            line = fd.readline()
            if line is None or line == '':
                break
            for item in json.loads(line):
                cnt += 1
                if cnt < start:
                    continue
                try:
                    url = item['url']
                    text = requests.get(url).text
                    pattern = re.compile(r'movieId=(\d+)"')
                    mid = pattern.findall(text)[0]
                    data = RottenTomatoesClient.get_movie_details(mid)
                    fd2 = open(str(cnt) + '.json', 'w')
                    fd2.write(json.dumps(data))
                    fd2.close()
                    print("done - ", cnt, mid)
                except Exception as e:
                    print(e)


def step3():
    """
    Input: json file list.
    
    1. Load json
    2. Extract useful information from json
    3. Store the data into csv
    :return: 
    """
    datas = []
    for i in range(1, 1611):
        fd = open(str(i) + '.json')
        j = json.load(fd)
        datas.append(j)
        fd.close()
    new_data = []
    for data in datas:
        critics_num_reviews = data['ratingSummary']['allCritics'].get('numReviews', 0)
        critics_score = data['ratings']['critics_score']
        critics_rating = data['ratings'].get('critics_rating', 'EMPTY')
        audience_num_total = data['ratingSummary']['audience']['numTotal']
        audience_score = data['ratings']['audience_score']
        audience_rating = data['ratings'].get('audience_rating', 'EMPTY')
        title = data['title']
        url = base_url + data['url']
        running_time = data.get('runningTime', 0)
        year = data['year']
        actors = []
        for j in data['casts']['castItems']:
            actors.append(j['person']['name'])
        actors = ','.join(actors)
        screenwriters = []
        for j in data['casts']['screenwriters']:
            screenwriters.append(j['name'])
        screenwriters = ','.join(screenwriters)
        directors = []
        for j in data['casts']['directors']:
            directors.append(j['name'])
        directors = ','.join(directors)
        producers = []
        for j in data['casts']['producers']:
            producers.append(j['name'])
        producers = ','.join(producers)

        genre1 = None
        genre2 = None
        genre3 = None
        for genre in data['genreSet']:
            if genre1 is None:
                genre1 = genre['displayName']
            elif genre2 is None:
                genre2 = genre['displayName']
            elif genre3 is None:
                genre3 = genre['displayName']
            else:
                break
        new_data.append({
            "title": title,
            "url": url,
            "running_time": running_time,
            "year": year,
            "critics_num_reviews": critics_num_reviews,
            "critics_score": critics_score,
            "critics_rating": critics_rating,
            "audience_num_total": audience_num_total,
            "audience_score": audience_score,
            "audience_rating": audience_rating,
            "actors": actors,
            "screenwriters": screenwriters,
            "directors": directors,
            "producers": producers,
            "genre1": genre1,
            "genre2": genre2,
            "genre3": genre3,
        })
    df = pd.DataFrame(new_data)
    df = df.drop_duplicates(['title'])
    df.to_csv('all-in-one.csv', index=False)
    return df


step1()
step2()
step3()
