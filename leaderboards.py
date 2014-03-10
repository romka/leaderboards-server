__author__ = 'Roman Aarkharov'

import simplejson as json
import time
from twisted.python import log
from twisted.internet.task import LoopingCall

from db import Db
from crypt import Crypt

class Leaderboards:
    """
      Main game class.
    """
    def __init__(self, max_clients, db_name, db_host, db_port, secret):
        """
            Constructor.
        """
        # self.server_status = 'not ready'
        self.db_name = db_name
        self.db_host = db_host
        self.db_port = db_port
        self.db_reconnect()

        # Restart DB connection in looping call
        self.lc = LoopingCall(self.db_reconnect)
        self.lc.start(300)


        # Sequence bellow showld be the same as on client application
        #self.sequence = [99, 143, 127, 182, 214, 17, 76, 92, 213, 199, 7, 43, 73, 197, 193, 5, 14, 88, 231, 94, 1, 183, 91, 191, 19, 237, 7, 85, 172, 41, 97, 29, 61, 111, 222]
        self.sequence = secret
        self.base64_alt = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

        log.msg(secret)

        self.apps = []
        self.clients = {}

        self.max_clients = max_clients

        # self.db = Db(self, db_name, db_host, db_port)
        self.crypt = Crypt(self.sequence)

    def db_reconnect(self):
        self.server_status = 'not ready'
        self.db = None
        self.db = Db(self, self.db_name, self.db_host, self.db_port)


    def _on_db_init_response(self, value, apps):
        """
            Callback for DB initialization function (class Db).
        """
        self.apps = apps
        if len(self.apps):
            self.server_status = 'ready'
            log.msg('DB connection established (updated)')

    def checkServerStatus(self):
        """
            Tis function calls from class LeaderboardsProtocol pn connectionMade method to check
            if server ready to process user data or not.
        """
        if self.server_status != 'ready' or len(self.clients) > self.max_clients:
            return False
        return True

    def initClient(self, client, addr):
        """
            Save connected user data.
        """

        client.client_id = addr.port
        client.host = addr.host

        client.server_status = self.server_status
        client.chunks_amount = None
        client.chunks = None
        client.data = ''


        client.mode = None
        client.game_type = None
        client.max_score = 0
        client.best_item = None
        client.top = []
        client.best_item_place = None


        log_msg = 'class Leadreboards, client %s initialized' % (client.client_id,)
        log.msg(log_msg)

        # Add new client to global dictionary
        self.clients[client.client_id] = client

        return client

    def processUserRecords(self, client_id, data):
        #log.msg('processUserRecords: received data')
        #log.msg(len(data))
        #log.msg(data)

        decoded_data = self.decodeUserRecords(data)

        #log.msg('decrypted')
        #log.msg(decoded_data)

        user_results = json.loads(decoded_data)

        self.clients[client_id].mode = mode = user_results.get('mode', None)
        self.clients[client_id].game_type = game_type = user_results.get('game_type', 'tetcolor')
        app_name = user_results.get('app_name', None)
        app_secret = user_results.get('app_secret', None)
        results = user_results.get('local_records', None)

        # TODO: uncomment this line after update of all clients
        # if game_type is None or mode is None or app_name is None or app_secret is None or results is None:
        if mode is None or app_name is None or app_secret is None or results is None:
            return 'wrong request'

        app_check = False
        for app in self.apps:
            if app['name'] == app_name and app['secret'] == app_secret:
                app_check = True

        if not app_check:
            return 'wrong arguments'

        #log.msg(app_name)
        #log.msg(app_secret)

        import base64

        items = []

        for result in results:
            if isinstance(result, dict):
                name = result.get('name', None)
                score = result.get('value', None)
                record_id = result.get('record_id', None)

                if name is not None and score is not None and record_id is not None:
                    #name = self.crypt(name, True)
                    name = base64.b64decode(name)

                    timestamp = int(time.time())

                    item = {}
                    item['name'] = name
                    item['score'] = score
                    item['timestamp'] = timestamp
                    item['record_id'] = record_id
                    if self.clients[client_id].game_type != 'tetcolor':
                        item['mode'] = self.clients[client_id].game_type + '_' + mode
                    else:
                        item['mode'] = mode

                    print('current best ' + str(self.clients[client_id].max_score) + '; score ' + str(score))
                    if int(score) > int(self.clients[client_id].max_score):
                        print('set this item as best because ' + str(score) + ' gt ' + str(self.clients[client_id].max_score))
                        self.clients[client_id].max_score = score
                        self.clients[client_id].best_item = item

                    items.append(item)

        self.db.check_unique_and_insert(items, self.clients[client_id].host)\
            .addCallback(self._on_db_insert_response, client_id)\
            .addErrback(self._on_db_error, client_id)

        return 'wait for db'

    def _on_db_insert_response(self, value, client_id):
        """
            Callback for DB insert function (class Db).
        """
        log.msg('Data inserted for client ' + str(client_id))

        self.retrieveTopResults(client_id)

    def retrieveTopResults(self, client_id):
        """
            Retrieve best results from DB and send to client,
        """

        self.db.get_top(client_id, self.clients[client_id].mode, self.clients[client_id].game_type)\
            .addCallback(self._on_db_get_top_response, client_id)\
            .addErrback(self._on_db_error, client_id)

    def _on_db_get_top_response(self, value, client_id):
        #log.msg('top10 number ' + str(len(self.clients[client_id].top)))
        #log.msg(str(self.clients[client_id].top[0]['name']))
        #for result in self.clients[client_id].top:
        #    log.msg('top item: ' + unicode(result['name']) + ' ' + str(result['score']))

        if self.clients[client_id].best_item is None or self.clients[client_id].best_item['score'] is None:
            score = 0
            self.clients[client_id].best_item = {}
            self.clients[client_id].best_item['score'] = 0
            self.clients[client_id].best_item['record_id'] = 'some-unexisting-value'
        else:
            score = self.clients[client_id].best_item['score']

        self.db.get_user_best(client_id, score, self.clients[client_id].mode, self.clients[client_id].game_type)\
            .addCallback(self._on_db_get_user_best_response, client_id)\
            .addErrback(self._on_db_error, client_id)

    def _on_db_get_user_best_response(self, value, client_id):
        log.msg('best score ' + str(self.clients[client_id].best_item['score']))
        log.msg('best id ' + self.clients[client_id].best_item['record_id'])
        log.msg('best place ' + str(self.clients[client_id].best_item_place))

        self.send_data_and_close_connection(client_id)


    def send_data_and_close_connection(self, client_id):
        result = {}
        result['top'] = self.clients[client_id].top
        result['place'] = self.clients[client_id].best_item_place

        j = json.dumps(result)
        c = self.crypt.crypt(j)

        self.clients[client_id].writeData(c)
        self.clients[client_id].transport.loseConnection()
        del self.clients[client_id]

    def _on_db_init_error(self, value):
        """
            DB initialization errorback.
        """
        log.msg('DB init errorback. Something went wrong in DB')

    def _on_db_error(self, value, client_id):
        """
            Errorback for client interaction with DB.
        """
        log.msg('DB errorback. Something went wrong in DB: ' + str(value))
        self.clients[client_id].writeData('4')
        self.clients[client_id].transport.loseConnection()

    def decodeUserRecords(self, data):
        log.msg('decodeUserRecords')
        return self.crypt.decrypt(data)

