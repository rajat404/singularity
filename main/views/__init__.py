from main import app
from main.views.admin import *

getdata = GetData()
app.add_route('/api/getdata/', getdata)

twitterauth = TwitterAuth()
app.add_route('/api/twitterauth', twitterauth)
