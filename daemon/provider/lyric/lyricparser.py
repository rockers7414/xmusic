
import pycurl

from io import BytesIO
from html.parser import HTMLParser

class LyricParser():

    # http status code
    HTTP_OK = 200

    # result_url
    __result_url = None
    # search _url
    __search_url = None

    # parse html parameters
    __target_container = None
    __target_attr = None
    __target_attr_value = None

    def __init__(self, result_url, search_url, target_container, target_attr, target_attr_value):
        self.__result_url = result_url
        self.__search_url = search_url
        self.__target_container = target_container
        self.__target_attr = target_attr
        self.__target_attr_value = target_attr_value

    def request(self, url):
        buf = BytesIO()
        client = pycurl.Curl()
        client.setopt(client.URL, url)
        client.setopt(client.WRITEFUNCTION, buf.write)
        client.setopt(pycurl.SSL_VERIFYPEER, 0)
        client.setopt(
            pycurl.USERAGENT, "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36")
        client.setopt(client.VERBOSE, True)
        client.perform()

        data = None
        if client.getinfo(pycurl.HTTP_CODE) == self.HTTP_OK:
            data = buf.getvalue().decode()

        client.close()
        buf.close()
        return data

    def gen_search_url(self, artist_name, track_name):
        artist_name = artist_name.strip().replace(" ", "-")
        track_name = track_name.strip().replace(" ", "-")
        return self.__search_url.format(track_name=track_name, artist_name=artist_name)

    def search_url_parse(self, page_data):
        raise NotImplementedError("search_url_parse is not implemented")

    def gen_result_url(self, artist_name, track_name):
        artist_name = artist_name.strip().replace(" ", "-")
        track_name = track_name.strip().replace(" ", "-")
        return self.__result_url.format(track_name=track_name, artist_name=artist_name)

    def result_url_parse(self, page_data):
        parser = LyricHTMLParser(
            self.__target_container, self.__target_attr, self.__target_attr_value)
        parser.feed(page_data)
        return parser.get_result()

    def etl_result(self, result):
        raise NotImplementedError("etl is not implemented")


class LyricHTMLParser(HTMLParser):

    # container
    __target_container = None

    # container indentity
    __target_attr = None
    __target_attr_value = None

    # flag for is target
    __is_target = False

    # result
    __result = ""

    def __init__(self, target_container, target_attr, target_attr_value):
        HTMLParser.__init__(self)
        self.__target_container = target_container
        self.__target_attr = target_attr
        self.__target_attr_value = target_attr_value

    def handle_starttag(self, tag, attrs):
        if tag == self.__target_container:
            for key, value in attrs:
                if key == self.__target_attr and value == self.__target_attr_value:
                    self.__is_target = True

    def handle_data(self, data):
        if self.__is_target:
            self.__result += "{0}".format(data)

    def handle_endtag(self, tag):
        if tag == self.__target_container:
            self.__is_target = False

    def get_result(self):
        if self.__result != "":
            return self.__result
        else:
            return None
