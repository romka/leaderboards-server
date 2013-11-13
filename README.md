Leaderboards server based on Twisted
====================================

To run this server yo need to have installed Python 2.7 or greater and Twisted 12 or greated (http://twistedmatrix.com/)

1. Change values of variables `host`, `port` and `http_port` in main.py to your own values.
2. Rename example_secret.py to secret.py and fill this file with your own values: each line of this file should contain one number from 1 to 255.
3. Run:
  * in console mode (for testing purposes): `twistd --nodaemon --python main.py`
  * in daemon mode (for production purposes): `twistd --python main.py`
