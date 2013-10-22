__author__ = 'Roman Arkharov'

from optparse import OptionParser

from serverfactory import LeaderboardsServerFactory

from twisted.application import internet, service
from twisted.python import log

# Rename example_secret.py to secret.py and fill it with your own values between 1 and 255
secret = [line.strip() for line in open('secret.py')]
log.msg(secret)

secret2 = []
for s in secret:
    secret2.append(int(s))

host = 'kece.ru'
port = 10088
http_port = 10089
max_clients = 10000

db_host = '10.20.2.105'
db_port = 27017
db_name = 'leaderboards'

top_service = service.MultiService()

leaderboards_service = service.Service()
leaderboards_service.setServiceParent(top_service)

log.msg('before init LeaderboardsServerFactory')
factory = LeaderboardsServerFactory(max_clients, leaderboards_service, db_name, db_host, db_port, secret2)
log.msg('after init LeaderboardsServerFactory')

tcp_service = internet.TCPServer(port, factory, interface=host)
tcp_service.setServiceParent(top_service)

# LeaderboardsWebserver should be imported after factory object creation
from http_responder import LeaderboardsWebserver
from twisted.web.server import Site

results = LeaderboardsWebserver(db_name, db_host, db_port)
results_factory = Site(results)
tcp_results_service = internet.TCPServer(http_port, results_factory, interface=host)
tcp_results_service.setServiceParent(top_service)

application = service.Application("main")

# this hooks the collection we made to the application
top_service.setServiceParent(application)
