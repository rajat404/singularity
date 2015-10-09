# from wsgiref import simple_server
from main import app
# if __name__ == '__main__':
#     httpd = simple_server.make_server('0.0.0.0', 9200, app)
#     httpd.serve_forever()
if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 9200, app, use_reloader=True)