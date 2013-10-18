__author__ = 'Roman Aarkharov'

import simplejson as json
import time
import txmongo
from twisted.python import log
from twisted.internet import defer


class Leaderboards:
    """
      Main game class.
    """
    def __init__(self, max_clients, db_name, db_host, db_port):
        self.server_status = 'not ready'
        self.sequence = [99, 143, 127, 182, 214, 17, 76, 92, 213, 199, 7, 43, 73, 197, 193, 5, 14, 88, 231, 94, 1, 183, 91, 191, 19, 237, 7, 85, 172, 41, 97, 29, 61, 111, 222]
        self.apps = []

        self.max_clients = max_clients
        self.db_name = db_name
        self.db_host = db_host
        self.db_port = db_port

        self.db_init().addCallback(self._on_db_init_response)

    @defer.inlineCallbacks
    def db_init(self):
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
    def db_insert(self, items):
        mongo = yield txmongo.MongoConnection(host=self.db_host, port=self.db_port)

        db = mongo[self.db_name]  # `foo` database
        records = db.records  # `test` collection

        # insert some data
        for item in items:
            log.msg('try to insert ' + item['name'] + ', ' + item['score'])
            result = yield records.insert({'name': item['name'], 'score': item['score'], 'timestamp': item['timestamp']}, safe=True)
            print result


    def _on_db_init_response(self, response):
        self.server_status = 'ready'

    def checkServerStatus(self):
        if self.server_status != 'ready':
            return False
        return True

    def initClient(self, client, addr):
        """
            Save connected user data.
        """

        client.client_id = addr.port

        client.server_status = self.server_status
        client.chunks_amount = None
        client.chunks = None
        client.chunks_amount = None
        client.data = ''

        log_msg = 'class Leadreboards, method initClient: %s, %s:%s' % (addr.type, addr.host, addr.port,)
        log.msg(log_msg)



        return client

    def saveUserRecords(self, data):
        log.msg('received data')
        log.msg(len(data))
        log.msg(data)

        decoded_data = self.decodeUserRecords(data)


        log.msg('decrypted')
        log.msg(decoded_data)

        user_results = json.loads(decoded_data)

        mode = user_results.get('mode', None)
        app_name = user_results.get('app_name', None)
        app_secret = user_results.get('app_secret', None)
        results = user_results.get('local_records', None)

        if mode == None or app_name == None or app_secret == None or results == None:
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
                timestamp = result.get('time', None)
                record_id = result.get('record_id', None)

                if name != None and score != None and record_id != None:
                    #name = self.crypt(name, True)
                    name = base64.b64decode(name)


                    timestamp = int(time.time())

                    item = {}
                    item['name'] = name
                    item['score'] = score
                    item['timestamp'] = timestamp

                    items.append(item)

        self.db_insert(items).addCallback(lambda ign: log.msg('Data inserted'))

    def decodeUserRecords(self, data):
        log.msg('decodeUserRecords')
        return self.crypt(data, True)

    def retrieveRecords(self):
        log.msg('retireved records')
        records = 'records list'
        return records

    def convert(self, byte, key, direction):
        new = ''
        if direction == False:
            new = byte + key
            if new > 255:
                new = new - 255
        else:
            new = byte - key
            if new < 0:
                new = new + 255
        return new
    
    def crypt(self, data, direction):
        result = ''
        max_counter = len(self.sequence)
        counter = 0

        if direction == False:
            for i in range(1, len(data)):
                ch = self.convert(ord(data[i, i]), self.sequence[counter], direction)
                ch = str(ch)
                while len(ch) < 3:
                    ch = '0' + ch

                result = result + ch

                counter = counter + 1
                if counter > max_counter:
                    counter = 1
        else:
            #log.msg('incoming data')
            #log.msg(len(data))
            #log.msg(data)
            xxx = ''
            for i in range(0, len(data), 3):
                ch = int(data[i: i + 3])
                ch2 = self.convert(ch, self.sequence[counter], direction)

                #xxx = xxx + ', ' + str(ch2)
                xxx = xxx + 'ch = ' + str(ch) + ', ch2 = ' + str(ch2) + ' ||| '

                result = result + chr(ch2)

                counter = counter + 1
                if counter >= max_counter:
                    counter = 0

            #log.msg('decrypted chars')
            #log.msg(xxx)

        return result
