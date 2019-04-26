#!/usr/bin/env python3
try:
    from bs4 import BeautifulSoup
    import urllib3
except ModuleNotFoundError:
    print("you need to install bs4 and urllib3 to use this script")
    exit(1)
    

import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import time



def lcs(s1, s2):
    matrix = [["" for x in range(len(s2))] for x in range(len(s1))]
    for i in range(len(s1)):
        for j in range(len(s2)):
            if s1[i] == s2[j]:
                if i == 0 or j == 0:
                    matrix[i][j] = s1[i]
                else:
                    matrix[i][j] = matrix[i-1][j-1] + s1[i]
            else:
                matrix[i][j] = max(matrix[i-1][j], matrix[i][j-1], key=len)

    cs = matrix[-1][-1]
    return len(cs)





def get_channel_vids_query(channel_url, query, poolmanager):
    query_url = channel_url + '/search?query=' + query.replace(' ', '&')
    while True:
        response = poolmanager.request('GET', query_url)
        if response.status == 200:
            break
        else:
            print("having trouble connecting to youtube")
            time.sleep(0.5)
    html = response.data

    channel_videos = []


    parsed_html = BeautifulSoup(html, features="html.parser")

    video_entries_html = parsed_html.body.findAll('li', attrs={'class':'feed-item-container'})

    author = parsed_html.body.find('a', attrs={'class':'branded-page-header-title-link'})['title']

    for video_entry_html in video_entries_html:
        video = {}
        video['title'] = video_entry_html.find('a', attrs={'class':'yt-uix-tile-link'})['title']
        video['id'] = video_entry_html.find('a', attrs={'class':'yt-uix-tile-link'})['href'].split('?v=')[1]
        video['author'] = author
        channel_videos.append(video)
    return channel_videos

def parse_sub_file(file):
    f = open(file, 'r')
    subs_xml = f.read()
    f.close()
    parsed_xml = BeautifulSoup(subs_xml, features="html.parser")
    subs_parsed_xml = parsed_xml.body.outline.findAll('outline')

    sub_channel_ids = [s['xmlurl'].split('channel_id=')[1] for s in subs_parsed_xml]
        
    return sub_channel_ids

def gen_channel_url(channel_id):
    return 'https://www.youtube.com/channel/' + channel_id

def gen_video_url(video_id):
    return 'https://www.youtube.com/watch?v=' + video_id

def search_in_subs(query, sub_file):
    subs = parse_sub_file(sub_file)
    print("the results printed last will be the closest to your query")
    print('Scanning Channels:')
    final_results = []
    future_channel_results = {}
    channel_result = [None]*len(subs)
    with ThreadPoolExecutor(max_workers=len(subs)) as executor:
        http = urllib3.PoolManager()
        for sid in range(len(subs)):
            sub_url = gen_channel_url(subs[sid])
            future_channel_results.update({executor.submit(get_channel_vids_query, sub_url, query, http): sid})
        c = 0
        for future in as_completed(future_channel_results):
            sid=future_channel_results[future]
            channel_result[sid] = future.result()
            print(c, "/", len(subs))
            c+=1
            
    for ch in channel_result:
        final_results += ch
    final_results = sorted(final_results, key=lambda x: lcs(x['title'].lower(), query.lower()))
    return final_results

def print_videos(query_results):
    for vid in query_results:
        print(vid['title'], 'by', vid['author'])
        print(gen_video_url(vid['id']))
        print()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("usage: yt-search-in-subs.py <query> <subscription file>")
        print("you can download the subscription file at:")
        print("https://www.youtube.com/subscription_manager?action_takeout=1")
        exit(1)
    elif not os.path.isfile(sys.argv[2]):
        print("subscription file not found")
        exit(1)
    else:
        now = time.time()
        result = search_in_subs(sys.argv[1], sys.argv[2])
        if result:
            print_videos(result)
        else:
            print("No videos found.")
        print(time.time() - now, "seconds for query")

