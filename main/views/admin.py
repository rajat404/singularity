import falcon
import json
import itertools
from time import time
from datetime import datetime
import copy
import networkx as nx
from bson.json_util import dumps as jsdumps

import urlparse
import oauth2 as oauth

# MongoDB Configuration
import pymongo
client = pymongo.MongoClient()
db = client.dedup

#custom module
import singular

# global variable required to share the request_token dict between multiple functions/classes
val = None

def valExchange(request_token):
    """
    To share the value of request_token in 2 functions
    """
    if request_token != 0:
        global val 
        val = request_token
        return True
    else:
        return (val)


def jaccard_set(s1, s2):
    """
    To find the nearly duplicate tweets
    """
    u = s1.union(s2)
    i = s1.intersection(s2)
    if len(u) != 0:
        return float(len(i)) / float(len(u))


def find_nodes(payload):
    """
    Using the network library, we find the transitive relation between the tweets, if any
    """
    g1 = nx.Graph(payload)
    o1 = nx.connected_components(g1)
    tempList = []
    for item in o1:
        tempList.append(item)
    return tempList


def get_ids(testing, refData):
    """
    Turns the index values to the tweet-IDs
    """
    finlist = []
    for item in testing:
        templist = []
        for i in range(len(item)):
            temp = str(refData[item[i]]['_id'])
            templist.append(temp)
        finlist.append(templist)
    return finlist


def cleanify(testing, refDict):
    """
    Returns the tweets corresponding to their tweet-IDs
    """
    finlist = []
    for item in testing:
        templist = []
        for i in item:
            templist.append(refDict[i])
        finlist.append(templist)
    return finlist


class GetData:

    """
    End point to fetch the data '/api/getdata/'
    """

    def on_get(self, req, resp, form={}, files={}):
        """
        Retrieves the data from MongoDB, analyzes it, and returns it in the GET call
        """
        start = time()
        # allTweets = db.refined.find()
        if form.get('authuser', None):
            authuser = form['authuser']
        else:
            resp.status = falcon.HTTP_200
            resp.content_type = "application/json"
            resp_dict = {"status": "failed", "summary": "Provide authuser var in URL",
                         "data": None
                         }
            resp.body = (json.dumps(resp_dict))
            return
        allTweets = db.refined.find({"authuser": { "$in": [authuser] } })

        data = []
        for item in allTweets:
            data.append(item)

        refData = copy.deepcopy(data)
        for item in refData:
            item['cleanWords'] = set(item['cleanWords'])

        # collections of only the 'clean' words of the tweets
        documents_straight = []
        for item in refData:
            documents_straight.append(item['cleanWords'])

        combinations = list(itertools.combinations([x for x in range(len(documents_straight))], 2))
        # compare each pair in combinations tuple of the sets of their words
        # Pairs of near-duplicates
        nearDupPartial = []
        # Pairs of exact duplicates
        exactDupPartial = []
        for c in combinations:
            jac = jaccard_set(documents_straight[c[0]], documents_straight[c[1]])
            if jac == 1:
                exactDupPartial.append(c)
            elif jac < 1 and jac >= 0.5:
                nearDupPartial.append(c)

        refDict = {}
        for item in refData:
            refDict[str(item['_id'])] = item

        nearDupList = find_nodes(nearDupPartial)
        exactDupList = find_nodes(exactDupPartial)
        tempNearDupList = get_ids(nearDupList, refData)
        tempExactDupList = get_ids(exactDupList, refData)
        finNearDupList = cleanify(tempNearDupList, refDict)
        finExactDupList = cleanify(tempExactDupList, refDict)

        stop = time()
        time_taken = stop - start
        response = {'exactCount': len(finExactDupList),
                    'nearCount': len(finNearDupList),
                    'tweetCount': len(refDict),
                    'allTweets': refDict,
                    'finExactDupList': finExactDupList,
                    'finNearDupList': finNearDupList,
                    'time_taken': time_taken
                    }

        if data == []:
            resp.status = falcon.HTTP_200
            resp.content_type = "application/json"
            resp_dict = {"status": "success", "summary": "No Tweets available",
                         "data": json.loads(jsdumps(data))
                         }
            resp.body = (json.dumps(resp_dict))
        else:
            resp.status = falcon.HTTP_200
            resp.content_type = "application/json"
            resp_dict = {"status": "success", "summary": "All tweets, exact-duplicates & near-duplicates",
                         "data": json.loads(jsdumps(response))
                         }
            resp.body = (json.dumps(resp_dict))




def getAppKeys():

    authtemp = db.appkeys.find()
    appkeys = {}
    for item in authtemp:
        appkeys = copy.deepcopy(item)

    consumer_key = appkeys['consumer_key']
    consumer_secret = appkeys['consumer_secret']
    return (consumer_key, consumer_secret)



class FindUser:

    """
    End point to check if the user exists in the system, and if so, get his/her credentials
    Endpoint: '/api/finduser/'
    """

    def on_get(self, req, resp, form={}, files={}):

        authuser = form['authuser']
        authval = None
        try:
            authtemp = db.users.find({"screen_name": { "$in": [authuser] } })          
            for item in authtemp:
                if item != None:
                    # Later, completely remove the authval statement, so that credentials don't get transfered to client side at all
                    authval = copy.deepcopy(item)
                    singular.fetch(str(authuser))
        except:
            pass

        # funcResponse = searchUser(authuser)
        if authval == None:
            resp.status = falcon.HTTP_200
            resp.content_type = "application/json"
            resp_dict = {"status": "success", "summary": "user not found",
                         "data": json.loads(jsdumps(False))
                         }
            resp.body = (json.dumps(resp_dict))
        else:
            resp.status = falcon.HTTP_200
            resp.content_type = "application/json"
            # resp_dict = {"status": "success", "summary": "OAUTH_TOKEN & other user details",
            #              "data": json.loads(jsdumps(authval))
            #              }
            resp_dict = {"status": "success", "summary": "User exists in DB, tweets extracted and saved",
                         "data": json.loads(jsdumps(True))
                         }
            resp.body = (json.dumps(resp_dict))



class CreateAuthUrl:
    """
    End point to get the auth_url for the user, so that it can be clicked, and we get the oauth keys
    Endpoint: '/api/createauthurl'
    """

    def on_get(self, req, resp, form={}, files={}):

        consumer_key, consumer_secret = getAppKeys()
        request_token_url = 'https://api.twitter.com/oauth/request_token'
        access_token_url = 'https://api.twitter.com/oauth/access_token'
        authorize_url = 'https://api.twitter.com/oauth/authenticate'
        consumer = oauth.Consumer(consumer_key, consumer_secret)
        client = oauth.Client(consumer)
        response, content = client.request(request_token_url, "GET")
        if response['status'] == '200':
            request_token = dict(urlparse.parse_qsl(content))
            finAuthUrl = authorize_url+'?oauth_token='+request_token['oauth_token']
            urlDict = {}
            urlDict['finAuthUrl'] = finAuthUrl
            valExchange(request_token)
            resp.status = falcon.HTTP_200
            resp.content_type = "application/json"
            resp_dict = {"status": "success", "summary": "auth_url",
                         "data": json.loads(jsdumps(finAuthUrl))
                         }
            resp.body = (json.dumps(resp_dict))
        else:
            resp.status = falcon.HTTP_400
            resp.content_type = "application/json"
            resp_dict = {"status": "success", "summary": "Check your consumer key & secret!",
                         "data": json.loads(jsdumps(None))
                         }
            resp.body = (json.dumps(resp_dict))



class AuthCallback:

    """
    End point to authorize the user and get his oauth_token & oauth_verifier
    Endpoint: '/api/authcallback'
    """

    def on_get(self, req, resp, form={}, files={}):

        # print form
        # response = form
        oauth_token = form['oauth_token']
        oauth_verifier = form['oauth_verifier']
        request_token = valExchange(0)
        consumer_key, consumer_secret = getAppKeys()
        request_token_url = 'https://api.twitter.com/oauth/request_token'
        access_token_url = 'https://api.twitter.com/oauth/access_token'
        authorize_url = 'https://api.twitter.com/oauth/authenticate'
        consumer = oauth.Consumer(consumer_key, consumer_secret)
        client = oauth.Client(consumer)
        token = oauth.Token(request_token['oauth_token'],
            request_token['oauth_token_secret'])
        token.set_verifier(oauth_verifier)
        client = oauth.Client(consumer, token)

        response, content = client.request(access_token_url, "POST")
        access_token = dict(urlparse.parse_qsl(content))
        temp = copy.deepcopy(access_token)
        temp['timestamp'] = datetime.now()
        try:
            db.users.insert(temp)
            # In order to avoid duplicates in the DB
            # currently the following statement isn't working
            # db.users.ensure_index([("screen_name", pymongo.ASCENDING), ("unique", True), ("dropDups", True)])
            # so in MongoDB shell, type:
            # db.users.ensureIndex({ screen_name : 1}, {unique:true, dropDups : true});
        except:
            pass
        resp.status = falcon.HTTP_200
        resp.content_type = "application/json"
        resp_dict = {"status": "success", "summary": "oauth_token & oauth_verifier",
                     "data": json.loads(jsdumps(access_token))
                     }
        resp.body = (json.dumps(resp_dict))
