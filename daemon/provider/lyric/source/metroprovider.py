import json
from provider.lyric.lyricparser import LyricParser
from decorator.singleton import singleton


@singleton()
class MetroProvider(LyricParser):

    # metro domain
    __metro_domain = "http://www.metrolyrics.com/"
    # metro result url
    __metro_lyrics_url = "http://www.metrolyrics.com/{track_name}-lyrics-{artist_name}.html"
    # metro search api
    __metro_lyrics_search_url = "http://api.metrolyrics.com/v1/multisearch/all/format/json?find={artist_name}-{track_name}"

    # parse html parameters
    __target_container = "div"
    __target_attr = "id"
    __target_attr_value = "lyrics-body-text"

    def __init__(self):
        LyricParser.__init__(self, self.__metro_lyrics_url,
                             self.__metro_lyrics_search_url, self.__target_container, self.__target_attr, self.__target_attr_value)

    def search_url_parse(self, page_data):
        jsonObj = json.loads(page_data)
        extract_data = jsonObj["results"]["songs"]["d"]
        url_list = []
        for item in extract_data:
            url_list.append(self.__metro_domain + item["u"])
        return url_list

    def etl_result(self, result):
        return result
