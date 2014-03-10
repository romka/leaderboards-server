__author__ = 'Roman Arkharov'

from twisted.web.resource import Resource
from pymongo import MongoClient
import simplejson as json


class LeaderboardsWebserver(Resource):
    isLeaf = True

    def __init__(self, db_name, db_host, db_port):
        self.db_name = db_name
        self.db_host = db_host
        self.db_port = db_port

    def render_GET(self, request):
        """
            Function returns top100 for every game mode in JSON format.
        """
        # Sync mongo connection
        sync_mongo = MongoClient(self.db_host, self.db_port)

        sync_db = sync_mongo[self.db_name]
        sync_records = sync_db.records

        result = {}

        modes = [
            'classic', 'relax', 'crazy',
            'tetcolor_columns_classic', 'tetcolor_columns_relax', 'tetcolor_columns_crazy',
            'tetcolor_mega_classic', 'tetcolor_mega_relax', 'tetcolor_mega_crazy',
            'tetcolor_tetris_classic', 'tetcolor_tetris_relax', 'tetcolor_tetris_crazy',
                 ]

        for mode in modes:
            r = []

            records = sync_records.find({'mode': mode, })\
                .sort([('score', -1)])\
                .limit(100)

            for item in records:
                r.append({
                    'name': item['name'],
                    'score': item['score'],
                    'timestamp': item['timestamp'],
                })

            result[mode] = r

        jsonp = json.dumps(result)
        jsonp = 'jsonCallback(' + jsonp + ');'

        request.setHeader('Content-Type', 'application/javascript')


        return jsonp
