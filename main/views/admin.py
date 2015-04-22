import falcon
import json
import itertools
from time import time
import copy
import networkx as nx
from bson.json_util import dumps as jsdumps


from requests_oauthlib import OAuth1
from urlparse import parse_qs, parse_qsl
from urllib import urlencode
import requests
from flask import request, redirect


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
        allTweets = db.refined.find()
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


class TwitterAuth:


    authval = json.load(open("authkeys.txt"))


    def on_get(self, req, resp, form={}, files={}):

        request_token_url = 'https://api.twitter.com/oauth/request_token'
        access_token_url = 'https://api.twitter.com/oauth/access_token'
        authenticate_url = 'https://api.twitter.com/oauth/authenticate'

        if request.args.get('oauth_token') and request.args.get('oauth_verifier'):
            auth = OAuth1(authval['TWITTER_CONSUMER_KEY'],
                          client_secret=authval['TWITTER_CONSUMER_SECRET'],
                          resource_owner_key=request.args.get('oauth_token'),
                          verifier=request.args.get('oauth_verifier'))
            r = requests.post(access_token_url, auth=auth)
            profile = dict(parse_qsl(r.text))

            user = User.query.filter_by(twitter=profile['user_id']).first()
            if user:
                token = create_token(user)
                return jsonify(token=token)
            u = User(twitter=profile['user_id'],
                     display_name=profile['screen_name'])
            db.session.add(u)
            db.session.commit()
            token = create_token(u)
            # return jsonify(token=token)
            resp.status = falcon.HTTP_200
            resp.content_type = "application/json"
            resp_dict = {"status": "success", "summary": "Behold the token!",
                         "token": json.loads(jsdumps(token))
                         }
            resp.body = (json.dumps(resp_dict))
        else:
            oauth = OAuth1(authval['TWITTER_CONSUMER_KEY'],
                           client_secret=authval['TWITTER_CONSUMER_SECRET'],
                           callback_uri=authval['TWITTER_CALLBACK_URL'])
            r = requests.post(request_token_url, auth=oauth)
            oauth_token = dict(parse_qsl(r.text))
            qs = urlencode(dict(oauth_token=oauth_token['oauth_token']))
            return redirect(authenticate_url + '?' + qs)