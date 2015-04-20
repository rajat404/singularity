import falcon
from wsgiref import simple_server

app = falcon.API()
# importing all the endpoints
from main.views import *

if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, app)
    httpd.serve_forever()
