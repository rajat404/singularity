import twitter
from datetime import datetime
from string import punctuation
import pymongo
import copy
import json

# List of stop words
stop = "about above across after afterwards again against all almost alone along already also although always am among amongst amoungst amount and another any anyhow anyone anything anyway anywhere are around as at back became because become becomes becoming been before beforehand behind being below beside besides between beyond bill both bottom but call can cannot cant computer con could couldnt cry describe detail do done down due during each eight either eleven else elsewhere empty enough etc even ever every everyone everything everywhere except few fifteen fify fill find fire first five for former formerly forty found four from front full further get give had has hasnt have hence her here hereafter hereby herein hereupon hers him his how however hundred indeed interest into its keep last latter latterly least less ltd made many may me meanwhile might mill mine more moreover most mostly move much must my name namely neither never nevertheless next nine nobody none noone nor not nothing now nowhere off often once one only onto other others otherwise our ours ourselves out over own part per perhaps please put rather same see seem seemed seeming seems serious several she should show side since sincere six sixty some somehow someone something sometime sometimes somewhere still such system take ten than that the their them themselves then thence there thereafter thereby therefore therein thereupon these they thick thin third this those though three through throughout thru thus together too top toward towards twelve twenty two under until upon very via was well were what whatever when whence whenever where whereafter whereas whereby wherein whereupon wherever whether which while whither who whoever whole whom whose why will with within without would yet you your yours yourself yourselves"


def sanitize(text, set_excludes):
    """
    Return a `sanitized` version of the string `text`.
    """
    text = text.lower()
    text = " ".join([w for w in text.split() if not ("http://" in w)])
    letters_noPunct = [(" " if c in set_excludes else c) for c in text]
    text = "".join(letters_noPunct)
    words = text.split()
    long_enuf_words = [w.strip() for w in words if len(w) > 1]
    return " ".join(long_enuf_words)


def Refine(raw_tweet, authuser):
    set_punct = set(punctuation)
    set_punct = set_punct - {"@"}
    simple = {}
    simple['authuser'] = authuser
    simple['text'] = raw_tweet['text']
    simple['cleanText'] = sanitize(raw_tweet['text'], set_punct)
    words = simple['cleanText']
    set_words = set(words.split())
    cleanWords = list(set_words)
    for term in cleanWords:
        if term in stop:
            cleanWords.remove(term)
    simple['cleanWords'] = set(cleanWords)
    simple['_id'] = raw_tweet['id']
    simple['user_screen_name'] = raw_tweet['user']['screen_name']
    simple['created_at'] = raw_tweet['created_at']
    simple['timestamp'] = datetime.now()
    simple['utc_timestamp'] = datetime.utcnow()
    try:
        simple['cleanUrl'] = raw_tweet['entities']['urls'][0]['expanded_url']
    except:
        simple['cleanUrl'] = None
    return simple


def main():
    # MongoDB Configuration
    client = pymongo.MongoClient()
    db = client.dedup
    # Taking the values from the DB, to be changed for generic users
    authtemp = db.appkeys.find()
    authval = {}
    for item in authtemp:
        authval = copy.deepcopy(item)

    CONSUMER_KEY = authval['CONSUMER_KEY']
    CONSUMER_SECRET = authval['CONSUMER_SECRET']
    OAUTH_TOKEN = authval['OAUTH_TOKEN']
    OAUTH_TOKEN_SECRET = authval['OAUTH_TOKEN_SECRET']
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
    t = twitter.Twitter(auth=auth)
    verificationDetails = t.account.verify_credentials()
    authuser = verificationDetails['screen_name']
    # Counter for the last tweet in our DB
    sinceCounter = None
    try:
        getLast = db.last.find().sort({_id: -1}).limit(1)
        for item in getLast:
            sinceCounter = item['lastTweet']
    except:
        pass

    if sinceCounter is None:
        completeTimeline = t.statuses.home_timeline(count=200)
    else:
        completeTimeline = t.statuses.home_timeline(count=200, since_id=sinceCounter)

    if(len(completeTimeline)) > 0:
        refinedTweet = []
        for tweet in completeTimeline:
            refinedTweet.append(Refine(tweet, authuser))

        # refining for inserting in MongoDB -- converting the set to list!
        mongoRefined = copy.deepcopy(refinedTweet)
        for item in mongoRefined:
            item['cleanWords'] = list(item['cleanWords'])

        # Refined Tweets are Cached in MongoDB
        currentCount = 0
        for item in mongoRefined:
            try:
                db.refined.insert(item)
            except:
                pass

        # Get the total number of tweets in refined collection
        try:
            currentCount = db.refined.count()
        except:
            pass
        lastTweet = completeTimeline[0]['id']
        endTweet = {'lastTweet': lastTweet, 'created_on': datetime.now(), 'currentCount': currentCount}
        db.last.insert(endTweet)

        # In order to avoid duplicates in the DB (just in case)
        db.refined.ensure_index([("_id", pymongo.ASCENDING), ("unique", True), ("dropDups", True)])

        # In order to expire documents after every 'n' hrs
        num_hrs = 10
        db.refined.ensure_index("utc_timestamp", expireAfterSeconds=num_hrs * 60 * 60)


if __name__ == '__main__':
    main()
