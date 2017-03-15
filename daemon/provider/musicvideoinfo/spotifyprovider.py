import logging
import pycurl
import json
import configparser

from urllib.parse import urlencode
try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

from database.entity import *
from .musicvideoinfoprovider import MusicVideoInfoProvider

class SpotifyProvider(MusicVideoInfoProvider):
    logger = logging.getLogger(__name__)

    service_host = "https://api.spotify.com"

    def getArtistsByName(self, artist_name):
        self.logger.info("Search the artist(" + artist_name + ") from Spotify.")

        offset = 0
        artists = []

        while True:
            params = {
                "q": artist_name,
                "type": "artist",
                "offset": offset,
                "limit": 50
            }

            buf = BytesIO()

            client = pycurl.Curl()
            client.setopt(pycurl.URL, self.service_host + "/v1/search" + "?" + urlencode(params))
            client.setopt(pycurl.WRITEFUNCTION, buf.write)
            client.perform()
            client.close()

            body = json.loads(buf.getvalue().decode("utf-8"))
            buf.close()

            if body["artists"]["total"] > 0:
                for artist_data in body["artists"]["items"]:
                    artist = Artist(artist_data["name"], artist_data["popularity"])

                    images = []
                    for image_data in artist_data["images"]:
                        images.append(Image(image_data["url"], image_data["width"], image_data["height"]))

                    genres = []
                    for genre in artist_data["genres"]:
                        genres.append(Genre(genre))

                    artist.images = images
                    artist.genres = genres

                    artists.append((artist_data["id"], artist))

            if body["artists"]["total"] > body["artists"]["limit"]:
                offset = offset + 1
            else:
                break

        return artists

    def getAlbumsByArtistId(self, artist_id):
        self.logger.info("Get albums of the artist(" + artist_id + ") from Spotify.")
        if not artist_id:
            return None

        offset = 0
        albums = []
        while True:
            params = {
                "album_type": "album",
                "offset": offset,
                "limit": 50
            }

            buf = BytesIO()

            client = pycurl.Curl()
            client.setopt(pycurl.URL, self.service_host + "/v1/artists/" + artist_id + "/albums" + "?" + urlencode(params))
            client.setopt(pycurl.WRITEFUNCTION, buf.write)
            client.perform()
            client.close()

            body = json.loads(buf.getvalue().decode("utf-8"))
            buf.close()

            if body["total"] > 0:
                for data in body["items"]:
                    album = Album(data["name"], None)

                    images = []
                    for image_data in data["images"]:
                        images.append(Image(image_data["url"], image_data["width"], image_data["height"]))
                    
                    album.images = images
                    
                    albums.append((data["id"], album))

            if body["total"] > body["limit"]:
                offset = offset + 1
            else:
                break

        return albums

    def getTracksByAlbumId(self, album_id):
        self.logger.info("Get tracks of the album(" + album_id + ") from Spotify.")
        if not album_id:
            return None

        offset = 0
        tracks = []
        while True:
            params = {
                "offset": offset,
                "limit": 50
            }

            buf = BytesIO()

            client = pycurl.Curl()
            client.setopt(pycurl.URL, self.service_host + "/v1/albums/" + album_id + "/tracks" + "?" + urlencode(params))
            client.setopt(pycurl.WRITEFUNCTION, buf.write)
            client.perform()
            client.close()

            body = json.loads(buf.getvalue().decode("utf-8"))
            buf.close()

            if body["total"] > 0:
                for data in body["items"]:
                    tracks.append(Track(data["name"], None, data["track_number"]))

            if body["total"] > body["limit"]:
                offset = offset + 1
            else:
                break

        return tracks

	def getNewRelease(self, offset_count, limit):
        self.logger.info("Get albums of the new release from Spotify.")
        service_host = "https://api.spotify.com"

        """
            Get client_id and client_secret value from local.
        """
        config = configparser.ConfigParser()
        config.read('../../config.cfg')
        client_id = config.get('SpotifyParameters', 'ClientID')
        client_secret = config.get('SpotifyParameters', 'ClientSecret')

        access_token = Spotify(client_id, client_secret).get_token()
        headers = ["Authorization: Bearer " + access_token]
        
        offset = 0
        while offset <= offset_count:
            params = {"offset": offset*limit, "limit": limit}
            buf = BytesIO()
            client = pycurl.Curl()
            client.setopt(pycurl.HEADER, False)
            client.setopt(pycurl.HTTPHEADER, headers)
            client.setopt(pycurl.URL, service_host + "/v1/browse/new-releases" + "?" + urlencode(params))
            client.setopt(pycurl.WRITEFUNCTION, buf.write)
#                 SSL certificate for Windows
#            client.setopt(pycurl.CAINFO, "C:\python3\curl\ca-bundle.crt")
            client.perform()
            client.close()
            body = json.loads(buf.getvalue().decode("utf-8"))
            buf.close()

            new_release = []
            for artist_data in body["albums"]["items"]:
                image = []
                for image_data in artist_data["images"]:
                    image.append((image_data["url"], image_data["width"], image_data["height"]))

                new_release.append((artist_data["id"], artist_data["type"], image))

            offset += 1

        return new_release
