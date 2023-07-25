from typing import Dict, List, Any
import glob
import json
import tqdm
from datetime import datetime
from dateutil.relativedelta import relativedelta

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

# constants
MIN_LISTEN_TIME = 30000
NOW = datetime(2023, 7, 1)
FILE_PATH : str = 'MyData/Streaming_History_Audio_*.json'

def load_files(path = FILE_PATH) -> List[Dict[str, int | bool | None]]:
    song_list = []
    
    for file in glob.glob(path):
        with open(file=file, mode='r', encoding='utf-8') as json_file:
            song_list += json.loads(json_file.read())
    
    return song_list

def parse_json(json_list : List[Dict[str, int | bool | None]]) -> Dict[str, int | bool | None]:

    all_songs = {}
    
    for song in tqdm.tqdm(json_list):
        
        # filter out podcasts, at least for now
        if song['spotify_track_uri'] == None:
            continue
        
        # if the song hasn't been seen before
        if song['spotify_track_uri'] not in all_songs:
            all_songs[song['spotify_track_uri']] = {
                'title'    : song['master_metadata_track_name'],
                'artist'   : song['master_metadata_album_artist_name'],
                'album'    : song['master_metadata_album_album_name'],
                'uri'      : song['spotify_track_uri'],
                'listens'  : [],
            }
        
        # add the data to the song
        all_songs[song['spotify_track_uri']]['listens'].append({
            'ts'           : datetime.strptime(song['ts'], '%Y-%m-%dT%H:%M:%SZ'),
            'time-played'  : song['ms_played'],
            'start-reason' : song['reason_start'],
            'end-reason'   : song['reason_end'],
            'shuffle'      : song['shuffle'],
            'skipped'      : song['skipped'],
            'offline'      : song['offline'],
            'incognito'    : song['incognito_mode'],
            'platform'     : song['platform'],
        })

    return all_songs

def filter_songs(songs : Dict[str, any],
                 ms_played = 0,
                 before = datetime.now(),
                 after = datetime.min,
                 artist_include = [],
                 artist_exclude = [],
                 start_reasons = [],
                 end_reasons = [],
                 on_shuffle = None,
                 while_offline = None,
                 skipped = None,
                 while_private = None,
                 ):
    
    filtered_songs = []
    continues = 0
    adds = 0
    
    for uri in tqdm.tqdm(songs): # iterate over every song
        
        song: Dict[str, any] = songs[uri]
        
        # sortable song object
        filtered_song = {
            # song info
            'title' : song['title'],
            'artist' : song['artist'],
            'album' : song['album'],
            'uri' : song['uri'],
            
            # sortable data
            'time-played' : [],
            'skips' : 0
        }
        
        # filter artists
        if artist_include != [] and song['artist'] not in artist_include: continues += 1; continue
        if song['artist'] in artist_exclude: continues += 1; continue
        
        # filter each listen
        for listen in song['listens']:
            
            # filter by listen time
            if listen['time-played'] < ms_played: continues += 1; continue
            
            # filter by timestamp
            if listen['ts'] > before: continues += 1; continue
            if listen['ts'] < after: continues += 1; continue
            
            # filter by start/end reason
            if start_reasons != [] and song['start-reason'] not in start_reasons: continues += 1; continue
            if end_reasons != [] and song['end-reason'] not in end_reasons: continues += 1; continue
            
            # boolean filters
            if listen['shuffle'] != on_shuffle and on_shuffle != None: continues += 1; continue
            if listen['offline'] != while_offline and while_offline != None: continues += 1; continue
            if listen['incognito'] != while_private and while_private != None: continues += 1; continue
            
            if listen['skipped']: filtered_song['skips'] += 1
            
            if listen['skipped'] != skipped and skipped != None: continues += 1; continue

            # add this listen
            adds += 1
            filtered_song['time-played'].append(listen['time-played'])

        # record the song
        filtered_songs.append(filtered_song)
    
    return filtered_songs

def sort(sort_by, songs):
    
    match sort_by:
        case 'plays':
            return sorted(songs, key=lambda song: len(song['time-played']), reverse=True)
        case 'time':
            return sorted(songs, key=lambda song: sum(song['time-played']), reverse=True)
        case 'skips':
            return sorted(songs, key=lambda song: song['skips'], reverse=True)
        case 'skip ratio':
            return sorted(songs, key=lambda song: (song['skips'] / len(song['time-played'])) if len(song['time-played']) != 0 else -1, reverse=True)

def ms_to_time(ms):
    s = ms // 1000
    
    hours = s // 3600
    minutes = (s // 60) % 60
    seconds = s % 60
    
    return f'{hours}:{"0" if minutes < 10 else ""}{minutes}:{"0" if seconds < 10 else ""}{seconds}'

def pretty_print(title : str, songs : List[Dict[str, int | bool | None]], count=10):
    print(f'{Fore.CYAN}{Style.BRIGHT}{title}')
    print(f'{Fore.BLUE}{Style.BRIGHT}  # : plays /     time / skips -> song')
    for i, song in enumerate(songs):
        rank: str = f'{Fore.YELLOW}{(i + 1):>3}{Fore.RESET}'
        plays: str = f'{Fore.CYAN}{Style.NORMAL}{len(song["time-played"]):>5}{Fore.RESET}'
        time: str = f'{Fore.CYAN}{Style.NORMAL}{ms_to_time(sum(song["time-played"])):>8}{Fore.RESET}'
        skips: str = f'{Fore.CYAN}{Style.NORMAL}{song["skips"]:>5}{Fore.RESET}'
        song_title: str = f'{Fore.LIGHTGREEN_EX}{song["title"]}{Fore.RESET}'
        song_artist: str = f'{Fore.MAGENTA}{song["artist"]}{Style.RESET_ALL}'
        
        print(f'{rank} : {plays} / {time} / {skips} -> {song_title} by {song_artist}')
        #print(f'{rank} : {plays} / {time} -> {song_title} by {song_artist}')
        
        if i+1 == count: break

if __name__ == '__main__':
    
    colorama_init()
    
    combined_json: Dict[str, any] = load_files()
    all_songs: Dict[str, any] = parse_json(combined_json)
        
    listened_to_first_half_of_2023 =        filter_songs(all_songs, ms_played=MIN_LISTEN_TIME, before=datetime.now(), after=datetime(2023, 1, 1), skipped=False)
    listened_to_past_year =                 filter_songs(all_songs, ms_played=MIN_LISTEN_TIME, after=datetime.now()-relativedelta(years=1))
    listened_to_first_half_of_2023_total =  filter_songs(all_songs, ms_played=MIN_LISTEN_TIME, before=datetime.now(), after=datetime(2023, 1, 1), skipped=False)
    listened_to_past_two_years =            filter_songs(all_songs, ms_played=MIN_LISTEN_TIME, after=datetime.now()-relativedelta(years=2), skipped=False)
    listened_to_all_time =                  filter_songs(all_songs, ms_played=MIN_LISTEN_TIME)
    listened_to_all_time_no_time_limit =    filter_songs(all_songs)
        
    pretty_print('Most played songs of 2023 by play count (unskipped)', sort('plays', listened_to_first_half_of_2023))
    pretty_print('Most played songs of 2023 by play count (total)', sort('plays', listened_to_first_half_of_2023_total))
    pretty_print('Most played songs of 2023 by time (total)', sort('time', listened_to_first_half_of_2023))
    #pretty_print('Most skipped songs of 2023', sort('skips', listened_to_first_half_of_2023))
    
    pretty_print('Most played songs of 2022-2023 by play count (unskipped)', sort('plays', listened_to_past_two_years))
    
    pretty_print('Most played songs of all time by play count (unskipped)', sort('plays', listened_to_all_time))
    pretty_print('Most played songs of all time by time (total)', sort('time', listened_to_all_time_no_time_limit))
    #pretty_print('Most skipped songs of all time', sort('skips', listened_to_all_time_no_time_limit))
    #pretty_print('Highest skips per play ratio of all time (total)', sort('skip ratio', listened_to_all_time), 500)
    #pretty_print('Highest skips per play ratio of all time (total)', sort('skip ratio', listened_to_all_time_no_time_limit), 1000)
        
    #listened_to_first_half_of_2023 = filter_songs(all_songs, ms_played=60000, before=NOW, after=datetime(2023, 1, 1))
    #listened_to_past_year = filter_songs(all_songs, ms_played=60000, after=NOW-relativedelta(years=1))
    #pretty_print('My most played songs of 2023 by play count', sort('plays', listened_to_first_half_of_2023), 20)
    #pretty_print('My most played songs of 2023 by time', sort('time', listened_to_first_half_of_2023), 20)
