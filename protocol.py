__author__ = 'Roman Arkharov'

from twisted.internet.protocol import Protocol
import time
import simplejson as json
from twisted.python import log

class LeaderboardsProtocol(Protocol):
    def connectionLost(self, reason):
        log.msg('LeaderboardsProtocol.connectionLost. Connection lost for client %s' % (self.client_id))
        # self.factory.Leaderboards_service.connectionClosedByClient(self.client_id)

    def connectionMade(self):
        """
            When user connected
        """
        log.msg('LeaderboardsProtocol.connectionMade. New connection %s, sending client_id to new client' % (self.client_id,))
        pass

    def dataReceived(self, raw_data):
        """
            Process data, received from user after connect.
        """
        self.factory.leaderboards_service.saveUserRecords(raw_data)

        records = self.factory.leaderboards_service.retrieveRecords()

        # Data to send
        self.writeData(records)
        self.transport.loseConnection()


    def writeData(self, data):
        self.transport.write(data + '\x00')
