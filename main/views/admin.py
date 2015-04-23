import falcon
import json
import itertools
from time import time
import copy
import networkx as nx
from bson.json_util import dumps as jsdumps

from rauth import OAuth1Service


# MongoDB Configuration
import pymongo
client = pymongo.MongoClient()
db = client.dedup

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

    CONSUMER_KEY = appkeys['CONSUMER_KEY']
    CONSUMER_SECRET = appkeys['CONSUMER_SECRET']
    return (CONSUMER_KEY, CONSUMER_SECRET)


def findUser(authuser):

    authval = {}
    try:
        authtemp = db.users.find({"authuser": { "$in": [authuser] } })          
        for item in authtemp:
            if item != None:
                authval = copy.deepcopy(item)
                return authval
            else:
                return None
    except:
        return None



def authorizeUser():

    CONSUMER_KEY, CONSUMER_SECRET = getAppKeys()
    twitter = OAuth1Service(
            name='twitter',
            consumer_key = CONSUMER_KEY,
            consumer_secret = CONSUMER_SECRET,
            request_token_url='https://api.twitter.com/oauth/request_token',
            access_token_url='https://api.twitter.com/oauth/access_token',
            authorize_url='https://api.twitter.com/oauth/authorize',
            base_url='https://api.twitter.com/1.1/')

    request_token, request_token_secret = twitter.get_request_token()
    authorize_url = twitter.get_authorize_url(request_token)
    return (authorize_url, request_token, request_token_secret)



class GetUrl:

    """
    End point to get authorize_url
    Endpoint: '/api/geturl/'
    """

    def on_get(self, req, resp, form={}, files={}):

        authorize_url, request_token, request_token_secret = authorizeUser()
        response = {
                    'authorize_url': authorize_url,
                    'request_token': request_token,
                    'request_token_secret': request_token_secret
                    }

        resp.status = falcon.HTTP_200
        resp.content_type = "application/json"
        resp_dict = {"status": "success", "summary": "authorize_url and other stuff",
                     "data": json.loads(jsdumps(response))
                     }
        resp.body = (json.dumps(resp_dict))


class SubmitPin:

    """
    End point to sumit PIN 
    Endpoint: '/api/submitpin/'
    Need request_token & request_token_secret as arguments along with the PIN
    """

    def on_get(self, req, resp, form={}, files={}):

        pin = form['pin']
        request_token = form['request_token'] 
        request_token_secret = form['request_token_secret'] 
        # print('Visit this URL in your browser: {url}'.format(url=authorize_url))
        # pin = input('Enter PIN from browser: ')
        # Get the PIN from the user, and submit here!
        CONSUMER_KEY, CONSUMER_SECRET = getAppKeys()
        twitter = OAuth1Service(
                name='twitter',
                consumer_key = CONSUMER_KEY,
                consumer_secret = CONSUMER_SECRET,
                request_token_url='https://api.twitter.com/oauth/request_token',
                access_token_url='https://api.twitter.com/oauth/access_token',
                authorize_url='https://api.twitter.com/oauth/authorize',
                base_url='https://api.twitter.com/1.1/')
        session = twitter.get_auth_session(request_token,
                request_token_secret,
                method='POST',
                data={'oauth_verifier': pin})
        oauthDict = {}
        oauthDict['OAUTH_TOKEN'] = session.access_token
        oauthDict['OAUTH_TOKEN_SECRET'] = session.access_token_secret

        # return (session.access_token, session.access_token_secret)
        resp.status = falcon.HTTP_200
        resp.content_type = "application/json"
        resp_dict = {"status": "success", "summary": "OAUTH_TOKEN & OAUTH_TOKEN_SECRET",
                     "data": json.loads(jsdumps(oauthDict))
                     }
        resp.body = (json.dumps(resp_dict))


class FindUser:

    """
    End point to check if the user exists in the system, and if so, get his/her credentials
    Endpoint: '/api/finduser/'
    """

    def on_get(self, req, resp, form={}, files={}):

        authuser = form['authuser']
        funcResponse = findUser(authuser)
        if funcResponse == None:
            resp.status = falcon.HTTP_200
            resp.content_type = "application/json"
            resp_dict = {"status": "success", "summary": "user not found",
                         "data": json.loads(jsdumps(None))
                         }
            resp.body = (json.dumps(resp_dict))
        else:
            resp.status = falcon.HTTP_200
            resp.content_type = "application/json"
            resp_dict = {"status": "success", "summary": "OAUTH_TOKEN & OAUTH_TOKEN_SECRET",
                         "data": json.loads(jsdumps(funcResponse))
                         }
            resp.body = (json.dumps(resp_dict))
