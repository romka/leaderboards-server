__author__ = 'Roman Aarkharov'

import simplejson as json
import time
from twisted.python import log

class Leaderboards:
    """
      Main game class.
    """
    def __init__(self, max_clients):
        self.clients = {}
        self.max_clients = max_clients

    def initClient(self, client, addr):
        """
            Save connected user data.
        """

        client.client_id = addr.port
        client.data = ['', 0]
        #client.status = 'waiting'
        #client.game_id = ''
        #self.clients[addr.port] = client
        # self.clients_waiting_list.append(addr.port)

        log_msg = 'class Leadreboards, method initClient: %s, %s:%s' % (addr.type, addr.host, addr.port,)
        log.msg(log_msg)

        return client

    def saveUserRecords(self, data):
        decoded_data = self.decodeUserRecords(data)
        log.msg('user data decoded')


    def decodeUserRecords(self, data):
        log.msg('decodeUserRecords')
        log.msg(data)

    def retrieveRecords(self):
        log.msg('retireved records')
        records = 'records list'
        return records
