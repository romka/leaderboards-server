__author__ = 'Roman Arkharov'

import optparse

from serverfactory import LeaderboardsServerFactory

from twisted.application import internet, service
from twisted.python import log


host = 'kece.ru'
port = 10088
max_clients = 10000

db_host = '10.20.2.105'
db_port = 27017
db_name = 'leaderboards'

top_service = service.MultiService()

leaderboards_service = service.Service()
leaderboards_service.setServiceParent(top_service)

log.msg('before init LeaderboardsServerFactory')
factory = LeaderboardsServerFactory(max_clients, leaderboards_service, db_name, db_host, db_port)
log.msg('after init LeaderboardsServerFactory')

tcp_service = internet.TCPServer(port, factory, interface=host)
tcp_service.setServiceParent(top_service)

application = service.Application("main")

# this hooks the collection we made to the application
top_service.setServiceParent(application)
