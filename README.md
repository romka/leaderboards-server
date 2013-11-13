Leaderboards server based on Twisted
====================================

To run this server yo need to have installed Python 2.7 or greater, Twisted 12 or greater (http://twistedmatrix.com/) and MongoDB 2.2 or greater.

1. Change values of variables `host`, `port`, `http_port`, `db_host`, `db_port` and `db_name` in main.py to your own values. MongoDB with async driver is used in this project.
2. Rename example_secret.py to secret.py and fill this file with your own values: each line of this file should contain one number from 1 to 255. This values must be the same as on client side.
3. In your db (`db_name`) you need to create an "apps" collection and put to this collection at least one value with your app name and secret (parameters `leaderboards_name` and `leaderboards_secret` in Gideros leaderboards example project). To do it you can run this command in Mongo console: `db.apps.insert({name: 'leaderboards_example', secret: 'Tratata-tratata-we-are-carry-the-cat'})`
4. Run:
  * in console mode (for testing purposes): `twistd --nodaemon --python main.py`
  * in daemon mode (for production purposes): `twistd --python main.py`

Example of client for this server you can find here: https://github.com/romka/leaderboards-gideros-client.

This server listens two ports: 
* first port (10088 by default) uses for recieve/send data to/from client, 
* second port (10089 by default) is a simple http-server which returns records list in JSONP format. It's might be useful for creating web-page with a records list.