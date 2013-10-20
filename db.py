__author__ = 'Roman Arkharov'

import txmongo
from pymongo import MongoClient
from twisted.internet import defer
from twisted.python import log

class Db:
    """
        Database communication class.
    """
    def __init__(self, parent, db_name, db_host, db_port):
        """
            Initialize variables.
        """
        self.db_status = 'not ready'

        self.parent = parent
        self.db_name = db_name
        self.db_host = db_host
        self.db_port = db_port

        self.apps = []

        self.init().addCallback(self.parent._on_db_init_response, self.apps).addErrback(self.parent._on_db_init_error)

    @defer.inlineCallbacks
    def init(self):
        """
            Get list of registered applications on server start.
        """
        mongo = yield txmongo.MongoConnection(host=self.db_host, port=self.db_port)

        db = mongo[self.db_name]  # `foo` database
        apps = db.apps  # `test` collection

        # fetch some documents
        items = yield apps.find(limit=10)
        for item in items:
            tmp = {}
            tmp['name'] = item['name']
            tmp['secret'] = item['secret']
            self.apps.append(tmp)

    @defer.inlineCallbacks
    def insert(self, items):
        """
            Try to put data to DB.
        """
        log.msg('class Db, method insert, items len ' + str(len(items)))

        # Async mongo connection
        async_mongo = yield txmongo.MongoConnection(host=self.db_host, port=self.db_port)

        # Sync mongo connection
        sync_mongo = MongoClient(self.db_host, self.db_port)

        async_db = async_mongo[self.db_name]
        async_records = async_db.records

        sync_db = sync_mongo[self.db_name]
        sync_records = sync_db.records

        # insert some data
        for item in items:
            log.msg('try to insert ' + item['name'] + ', ' + item['score'])
            #
            # This is a only one place with blocking request to DB, but I need this request to not insert
            # data twice.
            #
            # TODO: find the way to remove this blocking request.
            #
            count = sync_records.find(
                {
                    'record_id': item['record_id'],
                    'mode': item['mode'],
                    'score': int(item['score']),
                    'name': item['name'],
                }).count()

            if count == 0:
                value = yield async_records.insert(
                    {
                        'name': item['name'],
                        'score': int(item['score']),
                        'timestamp': item['timestamp'],
                        'record_id': item['record_id'],
                        'mode': item['mode'],
                    }, safe=True)
                log.msg('record inserted ' + item['record_id'])
            else:
                log.msg('record NOT inserted ' + item['record_id'])

    @defer.inlineCallbacks
    def get_top(self, client_id, mode):
        """
            Try to get top 10 from DB.
        """
        log.msg('class Db, method get_top, mode = ' + mode)

        # Async mongo connection
        async_mongo = yield txmongo.MongoConnection(host=self.db_host, port=self.db_port)
        async_db = async_mongo[self.db_name]
        async_records = async_db.records

        f = txmongo.filter.sort(txmongo.filter.DESCENDING('score'))

        import base64

        top10 = yield async_records.find({'mode': mode,}, filter=f, limit=10)
        for item in top10:
            name = item['name']
            name = name.encode('utf-8-sig')
            name = base64.b64encode(name)
            name = name.replace('77u/', '')

            tmp = {}
            tmp['name'] = name
            tmp['score'] = item['score']
            tmp['timestamp'] = item['timestamp']
            #log.msg(tmp)
            self.parent.clients[client_id].top.append(tmp)

    @defer.inlineCallbacks
    def get_user_best(self, client_id, score, mode):
        """
            Try to get top 10 from DB.
        """
        log.msg('class Db, method get_user_best')

        # Async mongo connection
        async_mongo = yield txmongo.MongoConnection(host=self.db_host, port=self.db_port)
        async_db = async_mongo[self.db_name]
        async_records = async_db.records

        best_place = yield async_records.find({'score': {'$gte': score,}, 'mode': mode,})
        count = 1
        for item in best_place:
            count += 1

        self.parent.clients[client_id].best_item_place = count
