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
        status = self.factory.leaderboards_service.checkServerStatus()
        if not status:
            log.msg('Server not ready')
            self.writeData(self.return_codes['server_not_ready'])
            self.transport.loseConnection()
        else:
            """
                Client cant send all data in one chunk because it might be too big. In this
                reason in first chunk user sends chunks amount (data splits to chunks by 1000 bytes), then
                user sends one or more data chunks which is concatenated in second part of this condition.
            """
            log.msg('chunks = ' + str(self.chunks) + '; amount = ' +  str(self.chunks_amount))

            if self.chunks_amount == None:
                # Receive amount of chunks in first packet
                self.chunks_amount = int(raw_data)
                self.chunks = 0
                log.msg('Client data separated to chunks: ' + str(self.chunks_amount))
                self.writeData('1')
            elif self.chunks < self.chunks_amount:
                # Concatenate all chunks
                self.chunks = self.chunks + 1
                self.data = self.data + raw_data
                self.writeData('1')

                log.msg('received chunk ' + str(self.chunks) + ' from ' + str(self.chunks_amount))

                # log.msg(raw_data)


            if self.chunks and self.chunks == self.chunks_amount:
                # Process received string
                log.msg('received fulls string')
                log.msg(self.data)
                result = self.factory.leaderboards_service.saveUserRecords(self.data)

                if result == 'wrong request':
                    log.msg('Wrong request')
                    self.writeData(self.return_codes['wrong_request'])
                    self.transport.loseConnection()
                elif result == 'wrong arguments':
                    log.msg('Wrong arguments')
                    self.writeData(self.return_codes['wrong_arguments'])
                    self.transport.loseConnection()
                else:
                    records = self.factory.leaderboards_service.retrieveRecords()

                    # Data to send
                    self.writeData(records)
                    self.transport.loseConnection()


    def writeData(self, data):
        #self.transport.write(data + '\x00')
        self.transport.write(data)
