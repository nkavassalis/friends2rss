#!/usr/bin/python

import requests
import requests.auth
import json
import datetime
import sys
reload(sys)

# fill me in!
clientid = ""
secret = ""
reddituser = ""
redditpass = ""

# set UTF-8, otherwise emoji being written to a file via stdout or pipe may barf 
sys.setdefaultencoding("UTF-8")

# get an auth token from reddit that we'll use to pull our friends list
# reddit has deprecated the non oAuth API methods
client_auth = requests.auth.HTTPBasicAuth(clientid, secret)
post_data = {"grant_type": "password", "username": reddituser, "password": redditpass}
headers = {"User-Agent": "friends2rss/1.0 by nkavassalis"}
response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
authresponse = response.json()

# get our friends submissions using the oAuth token we just got
# output is in JSON, most recent 25 submissions
auth = "%s %s" % (authresponse['token_type'], authresponse['access_token'])
headers = {"Authorization": auth, "User-Agent": "friends2rss/1.0 by nkavassalis"}
response = requests.get("https://oauth.reddit.com/r/friends/.json", headers=headers)
friends = response.json()['data']['children']

# lets create some lazy RSS
print "<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n<rss version=\"2.0\">"
print "<channel>\n\t<title>%s's Reddit friends feed</title>\n\t<link>http://reddit.com/r/friends</link>\n\t<description>%s's Reddit friends feed</description>" % (reddituser, reddituser)

for post in friends:
  print "\t<item>"
  print "\t\t<title>%s</title>" % post['data']['title']
  print "\t\t<category>%s</category>" % post['data']['subreddit']
  print "\t\t<author>%s@reddit (%s)</author>" % (post['data']['author'], post['data']['author'])
  print "\t\t<link>%s</link>" % post['data']['url']

  permalink = "https://reddit.com%s" % post['data']['permalink']

  if not post['data']['selftext_html'] and post['data']['media']:
    print "\t\t<description>&lt;a href='%s'&gt;&lt;img src='%s'&gt;&lt;/a&gt;&ltbr&gt;&lt;a href='%s'&gt;%s&lt;/a&gt;</description>" % (post['data']['url'], post['data']['media']['oembed']['thumbnail_url'], permalink, permalink)
  elif not post['data']['selftext_html']:
   print "\t\t<description>&lt;a href='%s'&gt;%s&lt;/a&gt;&ltbr&gt;&lt;a href='%s'&gt;%s&lt;/a&gt;</description>" % (post['data']['url'], post['data']['url'], permalink, permalink)
  else:
    print "\t\t<description>%s&ltbr&gt;&lt;a href='%s'&gt;%s&lt;/a&gt;</description>" % (post['data']['selftext_html'], permalink, permalink)

  print "\t\t<pubDate>%s</pubDate>" % datetime.datetime.fromtimestamp(int(post['data']['created_utc'])).strftime("%a, %d %b %Y %H:%M:%S +0000")
  print "\t</item>"

print "</channel>\n</rss>"

