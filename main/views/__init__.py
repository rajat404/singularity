from main import app
from main.views.admin import *

getdata = GetData()
app.add_route('/api/getdata/', getdata)

geturl = GetUrl()
app.add_route('/api/geturl/', geturl)

submitpin = SubmitPin()
app.add_route('/api/submitpin/', submitpin)

finduser = FindUser()
app.add_route('/api/finduser/', finduser)


