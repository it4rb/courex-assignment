import urllib2
import json

import time
from datetime import datetime
import dateutil.parser
from dateutil.relativedelta import relativedelta

# convert to github search format
def fmtTime(dt):
    return dt.isoformat().replace('+00:00', 'Z')

def getNextUrl(linkHeader):
    # TODO: find a more robust way to parse this
    if linkHeader is None:
        return None

    rels = linkHeader.split(', ')
    for rel in rels:
        comp = rel.split('; ')
        if len(comp) != 2:
            print 'error: invalid rel', rel
        r = comp[1].replace('rel="', '').replace('"', '')
        if r == 'next':
            return comp[0].replace('<', '').replace('>', '')
    # maybe there's no 'next' relation in the header
    return None

MAX_RESULT_AVAILABLE = 1000
SEARCH_URL_TMPL = 'https://api.github.com/search/users?q=location%3Asingapore+created%3A{}..{}&per_page=100'
AUTH_HEADER = {}
# authenticated user will have higher request limit
# AUTH_HEADER = {"Authorization": "token <...>"}

def getUsersCreatedWithin(begin, end):
    url = SEARCH_URL_TMPL.format(fmtTime(begin), fmtTime(end))
    usernames = []
    while url != None:
        print url
        response = urllib2.urlopen(urllib2.Request(url, headers=AUTH_HEADER))
        result = json.load(response)

        # total results for all pages within period
        total = result['total_count']
        if total > MAX_RESULT_AVAILABLE:
            # TODO: gracefully decrease search period and try again
            print 'error: too much:', total, url

        for x in result['items']:
            usernames.append(x['login'])

        # get next page Url, or None in case finished for this period
        url = getNextUrl(response.info().getheader('Link'))

        # check limit and wait if exceeded
        remaining = int(response.info().getheader('X-RateLimit-Remaining'))
        if remaining < 1:
            # sleep until gaining enough limit
            resetTime = int(response.info().getheader('X-RateLimit-Reset'))
            current = int(time.time())
            waitTime = resetTime - current + 1
            print 'waiting for limit in {} seconds'.format(waitTime)
            time.sleep(waitTime)

    return usernames

def getUsers(fd):
    # first user was created in 2017
    begin = dateutil.parser.parse('2007-01-01T00:00:00Z')
    # search for each 6 months, so that the number of result won't exceed 1k limit
    step = relativedelta(months=6)

    curYear = datetime.now().year
    totalCount = 0
    while begin.year <= curYear:
        end = begin + step
        users = getUsersCreatedWithin(begin, end)

        # print 'fetched {} users between {} .. {}'.format(len(users), begin, end)
        for user in users:
            fd.write(user + '\n')
        totalCount += len(users)

        # increase to next period and try again
        begin = end + relativedelta(seconds=1)

if __name__ == "__main__":
    with open('github_singapore_users.txt', 'w') as fd:
        getUsers(fd)
