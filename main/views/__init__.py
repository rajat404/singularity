from main import app
from main.views.admin import *

getdata = GetData()
app.add_route('/api/getdata/', getdata)

finduser = FindUser()
app.add_route('/api/finduser/', finduser)

authcallback = AuthCallback()
app.add_route('/api/authcallback', authcallback)

createauthurl = CreateAuthUrl()
app.add_route('/api/createauthurl', createauthurl)
