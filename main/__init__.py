import falcon
from wsgiref import simple_server
from falcon.util.uri import parse_query_string

def generate_formdata(req, resp, params):
    """sets prarams['form'] to pass to every endpoint.
    """
    #print "here"
    form = dict()
    files = dict()
    if req.method == 'GET':
        di = parse_query_string(req.query_string)
        form = dict(di)
        params['form'], params['files'] = dict(form), dict(files)
    return True

app = falcon.API(before=[generate_formdata])
# importing all the endpoints
from main.views import *

# if __name__ == '__main__':
#     httpd = simple_server.make_server('127.0.0.1', 8000, app)
#     httpd.serve_forever()
