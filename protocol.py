__author__ = 'Roman Arkharov'

from twisted.internet.protocol import Protocol
import time
import simplejson as json
from twisted.python import log

class LeaderboardsProtocol(Protocol):
    return_codes = {}
    return_codes['wrong_request'] = '1'
    return_codes['wrong_arguments'] = '2'
    return_codes['server_not_ready'] = '3'
    return_codes['unhandled_situation'] = '4'

    def connectionLost(self, reason):
        log.msg('LeaderboardsProtocol.connectionLost. Connection lost for client %s' % (self.client_id))
        # self.factory.Leaderboards_service.connectionClosedByClient(self.client_id)

    def connectionMade(self):
        """
            When user connected
        """
        log.msg('LeaderboardsProtocol.connectionMade. New connection %s, sending client_id to new client' % (self.client_id,))

        status = self.factory.leaderboards_service.checkServerStatus()
        if not status:
            log.msg('Server not ready ' + str(self.return_codes['server_not_ready']))
            self.writeData(self.return_codes['server_not_ready'])
            self.transport.loseConnection()

    def dataReceived(self, raw_data):
        """
            Process data, received from user after connect.

            Client can't send all data in one chunk because it might be too big. In this
            reason in first chunk user sends chunks amount (data splits to chunks by 1000 bytes), then
            user sends one or more data chunks which is concatenated in second part of this condition.
        """
        #log.msg('chunks = ' + str(self.chunks) + '; amount = ' +  str(self.chunks_amount))
        #log.msg('chunks = ' + str(self.chunks) + '; amount = ' +  str(self.chunks_amount))

        if self.chunks_amount == None:
            # First data-packet always should contain only one number - number of data chunks.
            self.chunks_amount = int(raw_data)
            self.chunks = 0
            log.msg('Client data separated to chunks: ' + str(self.chunks_amount))
            self.writeData('1')
        elif self.chunks < self.chunks_amount:
            # Every next data-packet should contain chunk of data.
            # Concatenate all chunks
            self.chunks = self.chunks + 1
            self.data = self.data + raw_data
            self.writeData('1')

            #log.msg('received chunk ' + str(self.chunks) + ' from ' + str(self.chunks_amount))

            # log.msg(raw_data)

        if self.chunks and self.chunks == self.chunks_amount:
            # Process received string, if delivered all data chunks.
            #log.msg('received fulls string')
            #log.msg(self.data)
            result = self.factory.leaderboards_service.processUserRecords(self.client_id, self.data)

            if result == 'wrong request':
                log.msg('Wrong request')
                self.writeData(self.return_codes['wrong_request'])
                self.transport.loseConnection()
            elif result == 'wrong arguments':
                log.msg('Wrong arguments')
                self.writeData(self.return_codes['wrong_arguments'])
                self.transport.loseConnection()
            elif result == 'wait for db':
                log.msg('Wait for db')
            else:
                # Unhandled situation. Break connection.
                log.msg('Unhandled situation, brake connection')
                self.writeData(self.return_codes['unhandled_situation'])
                self.transport.loseConnection()


    def writeData(self, data):
        #self.transport.write(data + '\x00')
        #log.msg('data for user ' + data)
        self.transport.write(data)
