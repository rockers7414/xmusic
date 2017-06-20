import glob
import importlib
import inspect
from os.path import dirname, join, basename, isfile
from inspect import isclass
from .lyricprovider import LyricProvider
from decorator.singleton import singleton


@singleton()
class Lyric(LyricProvider):

    __module_prefix = "provider.lyric.source"
    __lyric_providers = []

    def __init__(self):
        self.load_source()

    def get_lyric(self, artist_name, track_name):

        if len(self.__lyric_providers) < 0:
            return None
        else:
            for module in self.__lyric_providers:
                # gen result url
                result_url = module.gen_result_url(artist_name, track_name)
                # request result url
                page_data = module.request(result_url)
                if page_data is not None:
                    # extract lyric
                    result = module.result_url_parse(page_data)
                    etl_data = module.etl_result(result)
                    return etl_data
                else:
                    # gen search url
                    search_url = module.gen_search_url(
                        artist_name, track_name)
                    search_page_data = module.request(search_url)
                    result_url_list = module.search_url_parse(
                        search_page_data)
                    if result_url_list is not None:
                        for url in result_url_list:
                            _page_data = module.request(url)
                            # extract lyric
                            result = module.result_url_parse(_page_data)
                            etl_data = module.etl_result(result)
                            if etl_data is not None:
                                return etl_data

    def load_source(self):
        path = join(dirname(__file__), "source/*")
        files = glob.glob(dirname(path) + '/*.py')

        for f in files:
            if isfile(f) and not f.endswith('__init__.py'):

                module_name = '{}.{}'.format(
                    self.__module_prefix, basename(f)[:-3])
                module = importlib.import_module(module_name)
                for key, value in inspect.getmembers(module):
                    if inspect.isclass(value):
                        if value.__module__.startswith(self.__module_prefix):
                            # init class
                            self.__lyric_providers.append(value())
