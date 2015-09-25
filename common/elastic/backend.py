from haystack.backends.elasticsearch_backend import ElasticsearchSearchBackend, ElasticsearchSearchEngine
    # FIELD_MAPPINGS

# FIELD_MAPPINGS['ngram'] = {'type': 'string', 'index_analyzer': 'str_index_analyzer',
#                            'search_analyzer': 'str_search_analyzer'}
#

class CustomElasticsearchBackend(ElasticsearchSearchBackend):
    def __init__(self, connection_alias, **connection_options):
        self.DEFAULT_SETTINGS['settings']['analysis']['analyzer']['str_search_analyzer'] = {
            'tokenizer': 'whitespace',
            'filter': ['lowercase']
        }

        self.DEFAULT_SETTINGS['settings']['analysis']['analyzer']['str_index_analyzer'] = {
            'tokenizer': 'keyword',
            'filter': ['lowercase', 'substring']
        }

        self.DEFAULT_SETTINGS['settings']['analysis']['filter']['substring'] = {
            'type': 'nGram',
            'min_gram': 3,
            'max_gram': 20
        }
        super(CustomElasticsearchBackend, self).__init__(connection_alias, **connection_options)


class CustomElasticsearchSearchEngine(ElasticsearchSearchEngine):
    backend = CustomElasticsearchBackend