__author__ = 'Roman Arkharov'

from twisted.internet.protocol import ServerFactory

from protocol import LeaderboardsProtocol
from leaderboards import Leaderboards

from twisted.python import log


class LeaderboardsServerFactory(ServerFactory):

    protocol = LeaderboardsProtocol

    def __init__(self, max_clients, service):
        """
          Server factory constructor
        """
        log.msg('Leaderboards server initialized')

        # parameters#
        self.leaderboards_service = Leaderboards(max_clients)
        self.service = service

    def buildProtocol(self, addr):
        """
          This method calls when new client connected
        """
        p = self.protocol()
        p.factory = self

        p = self.leaderboards_service.initClient(p, addr)

        log.msg('class LeaderboardsServerFactory, method buildProtocol: protocol was built')

        return p
