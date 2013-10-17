__author__ = 'Roman Arkharov'

import optparse

from serverfactory import LeaderboardsServerFactory

from twisted.application import internet, service


host = 'kece.ru'
port = 10088
max_clients = 10000

top_service = service.MultiService()

leaderboards_service = service.Service()
leaderboards_service.setServiceParent(top_service)

factory = LeaderboardsServerFactory(max_clients, leaderboards_service)
tcp_service = internet.TCPServer(port, factory, interface=host)
tcp_service.setServiceParent(top_service)

application = service.Application("main")

# this hooks the collection we made to the application
top_service.setServiceParent(application)
