from main import app
from main.views.admin import *

getdata = GetData()
app.add_route('/api/getdata/', getdata)
