__author__ = 'Roman Arkharov'

from twisted.internet.protocol import ServerFactory

from protocol import LeaderboardsProtocol
from leaderboards import Leaderboards

from twisted.python import log

log.msg('LeaderboardsServerFactory')

class LeaderboardsServerFactory(ServerFactory):

    protocol = LeaderboardsProtocol

    def startFactory(self):
        self.leaderboards_service = Leaderboards(self.max_clients, self.db_name, self.db_host, self.db_port)

    def __init__(self, max_clients, service, db_name, db_host, db_port):
        """
          Server factory constructor
        """

        self.service = service
        self.max_clients = max_clients
        self.db_name = db_name
        self.db_host = db_host
        self.db_port = db_port

        log.msg('Leaderboards server initialized')

    def buildProtocol(self, addr):
        """
          This method calls when new client connected
        """
        p = self.protocol()
        p.factory = self

        p = self.leaderboards_service.initClient(p, addr)

        log.msg('class LeaderboardsServerFactory, method buildProtocol: protocol was built')

        return p
