# open get html of beatport top 100 dnb
# put artists and songs to dictionary 'artist:song' or add to db
# if song not already in db

import json
import os
import time
import requests
from bs4 import BeautifulSoup
from secrets import spotify_token, spotify_user_id
from datetime import datetime
from exceptions import ResponseException



class CreatePlaylist:
    
    def __init__(self):
        self.all_song_info = {}
        

    def get_artists_and_songs(self):
        fav_artists = ['Rockwell', 'Mefjus', 'Break', 'S.P.Y', 'Benny L', 'Alix Perez', 'Rene Lavice', 'Enei', 'Upgrade (UK)', 'Netsky']
        url = "https://www.beatport.com/genre/drum-and-bass/1/top-100"
        r = requests.get(url)
        soup = BeautifulSoup(r.text,'html.parser')
        records = soup.findAll('div', {'class','buk-track-meta-parent'})

        for record in records:
            artist_name = record.find('p', {'class', 'buk-track-artists'}).text
            if ',' in artist_name:
                new = artist_name.split(',')
                artist_name = new[0].strip()
            song_name = record.find('span', {'class','buk-track-primary-title'}).text

            if song_name is not None and artist_name is not None:
                if artist_name.strip() in fav_artists:
                    self.all_song_info[song_name] = {
                        "song_name": song_name.strip(),
                        "artist_name": artist_name.strip(),

                        # add the uri, easy to get song to put into playlist
                        "spotify_uri": self.get_spotify_uri(song_name, artist_name)
                    }
                    print(song_name,artist_name)
                        #print(self.all_song_info)

            
                
    def get_spotify_uri(self, song_name, artist_name):

        """Search For the Song"""

        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(
            song_name,
            artist_name
        )
        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]
        # only use the first song
        uri = songs[0]["uri"]
        return uri


    def create_playlist(self):
        """Create A New Playlist"""
        now = datetime.now()
        playlist_name =  "Beatport dnb " + now.strftime("%d/%m/%Y")
        request_body = json.dumps({
            "name": playlist_name,
            "description": "pick of favourite artists from top100 dnb",
            "public": True
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(
            spotify_user_id)
        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)})


        response_json = response.json()
        return response_json["id"]

    def testing(self):

        try:
            self.get_artists_and_songs()
            uris = [info["spotify_uri"]
                    for song, info in self.all_song_info.items()]
            playlist_id = self.create_playlist()
            request_data = json.dumps(uris)
            query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
                playlist_id)

            response = requests.post(
                query,
                data=request_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {}".format(spotify_token)
                }
            )
            response_json = response.json()
            return response_json
        except Exception as e:
            print(e)





if __name__ == '__main__':
    cp = CreatePlaylist()
    cp.testing()