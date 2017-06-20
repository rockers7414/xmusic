from decorator.singleton import singleton
from provider.lyric.lyricparser import LyricParser
from html.parser import HTMLParser


@singleton()
class GeniusProvider(LyricParser):

    # genius domain
    __genius_domain = "https://genius.com/"
    # genius result url
    __genius_lyrics_url = "https://genius.com/{artist_name}-{track_name}-lyrics"
    # genius search api
    __genius_lyrics_search_url = "https://genius.com/search?q={artist_name}-{track_name}"

    # parse html parameters
    __target_container = "div"
    __target_attr = "class"
    __target_attr_value = "lyrics"

    def __init__(self):
        LyricParser.__init__(self, self.__genius_lyrics_url,
                             self.__genius_lyrics_search_url, self.__target_container, self.__target_attr, self.__target_attr_value)

    def search_url_parse(self, page_data):
        parser = self.LyricSearchHTMLParser()
        parser.feed(page_data)
        return parser.get_result()

    def etl_result(self, result):
        return result

    class LyricSearchHTMLParser(HTMLParser):
        # container
        __target_container = "a"

        # container indentity
        __target_attr = "class"
        __target_attr_value = " song_link"

        # result attr key
        __result_attr_key = "href"

        # result
        __result = []

        def handle_starttag(self, tag, attrs):
            if tag == self.__target_container:
                for key, value in attrs:
                    if key == self.__target_attr and value == self.__target_attr_value:
                        for _key, _value in attrs:
                            if(_key == self.__result_attr_key):
                                self.__result.append(_value)

        def get_result(self):
            if len(self.__result) > 0:
                return self.__result
            else:
                return None
