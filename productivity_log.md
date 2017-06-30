# Productivity log
## Contents
- [Week 1](#week-1)
- [Week 2](#week-2)
- [Week 3](#week-3)
- [Week 4](#week-4)
- [Week 5](#week-5)
- [Week 6](#week-6)
- [Week 7](#week-7)
- [Week 8](#week-8)
## Week 1
### 3-4-2017
Read documentation of different crawler frameworks and applications. Explored options are Selenium, WebPageTest, LightBeam and XTest.
It turned out that if we would use LightBeam, we might as well adapt the Privacy Badger source code for this purpose, as Privacy Badger already detects cookies, and as both are browser extensions, there is no need to start from scratch.
I will try to implement some basic stuff in Mechanize (python library) as well, to see what results we can get without using an actual browser.

### 4-4-2017
Meeting with Maarten, adapted Privacy Badger source code so that it does not block any cookies, but just detects them. Source code is up on this repo, tried it by installing it into a fresh google chrome. Do not know about firefox.

Next step is logging the found cookies, which potentially means we have to extract more data than Privacy Badger is currently storing.
useful stuff here: https://developer.chrome.com/apps/app_codelab_filesystem

Turns out the above is only allowed for apps, not extensions. The easiest solution for this problem (especially seeing that we would like to do this in parallel in the future)
is setting up a localhost server that will save the data on a POST request.

### 5-4-2017
I have found that cookies are filtered from the incoming responses in webrequest.js:216. If I now log them to some global variable,
I should be able to write the contents of the "set-cookie" fields to the disk for later analysis.

Disabled cookie filtering in http responses, and log them to console. I also disabled the outgoing http request filtering (by default, it removes the referer and sent cookies).

No longer log inbound http responses, because when they contain cookies, we can assume that these cookies are also sent out at some point. I have chosen to log the outbound cookies rather than inbound
set-cookie requests, because I discovered that the inbound cookies did not cover all cookies that are displayed in the Privacy Badger Snitch map. Note that in fact, the snitch map is already exactly what we want:
it links a domain to its third party cookie domains. However, because it is linked the wrong way around (every third party has a list of the first party domains we encountered it on), it seemed a good solution for now
to just make a new log. Originally, I also intended for this log to also contain the fields of the "set-cookie", but that is too in-depth for now, and reduces clarity.

In the end, I decided to just display the snitchmap, and not do any manual logging (it is still there, but we do not display it anymore). For comparing the frameworks, the snitch_map will do just fine. Therefore,
the incoherent brabbling above can be ignored. Furthermore, I have taken a look at cookie/script detection, but I could not find out whether Privacy Badger also investigates scripts or not. It seems the 
"fingerprinting" detection does something with scripts, but it is never triggered on the test cases. It also seems that at some point in the files, PB does do some local storage analyzation, but for now, I
cannot easily change it do detect first party cookies.

It seems that the snitchmap does not contain the elements that are listed under "Vooralsnog lijkt het erop dat de volgende (derde) partijen u niet volgen". We will have to look into this 
if we decide to use privacy badger.


It turns out that mechanize does not support python 3. While that is not really a problem, it got me thinking about using the library, and I have decided that there is no point. The comparison
we want to make here is if we can find as many details of the cookies with a simple crawler script as with running a full automated browser. As Mees already implemented Scrapy, there is no point
in also implementing something in Mechanize.

Added onCookieChanged listener to the PB extension. For now, it logs just the domain and whether it is a private cookie (not cross-site), but more info is available.
Have been fucking around with content scripts to find some automated way of accessing the DOMtree of every page, only to realize that automation is not relevant at this point.
I ended up adding another function "findURLs" to the badger class, which is called when the "save logs" button is pressed.

### 6-4-2017
I have decided not to implement the URL finding part, because Mees already has some working version of it in Python. While that is a different language, 
it is simply a specific RegExp that will target those fields that are interesting to us. Because I can now access the DOM tree, I could convert it to a string
and run the exact same RegExp on it, so there is no need for me to create my own implementation of the URL finding algorithm.

Read article about tracking by using CSS to determine whether a user has visited a link.
Furthermore, [this](http://www.franziroesner.com/pdf/webtracking-NSDI2012.pdf) article mentions that *"However, in most browsers,
third-party cookie blocking applies only to the setting,
not to the sending, of cookies (in Firefox, it applies to
both)"*. Apparently, browsers already have a built-in option that should disable third party cookies. I have explored Chrome's options and confirmed that this setting is there. Chrome also has a setting that deletes all cookies when the browser is closed. 

Following the categories as explained in the article, it seems like successfully disabling third-party cookies should stop trackers from using cookies to cross-site identify the user, except in those cases where the tracker opens a popup window, setting its own first-party cookie (or, for that matter, sites like Facebook, that the user has visited intentionally).


### 7-4-2017
Meeting with Martin, Hosein and Mees to further define what exactly it is we are going to do the following weeks. Concluding the meeting, I have drastically changed the focus of my research and thesis.
I will skip the improved classification altogether, and instead try to crawl roughly 5 million websites within feasible time. In this crawl, I will collect third-party cookie domains on each 
page and use them in the community clustering algorithm. The amount of depth in this analysis will be determined by the required execution time, which should be sufficient to reach the 5 million websites.

## Week 2
### 10-4-2017
Refining roadmap, add to github rather than google docs

Found [redditlist](http://redditlist.com/), which gives overview of the amount of subs per reddit. Can filter on NSFW so we can leave out porn reddits, great! However, because this simply displays them by ranking, we cannot get a full 
overview (i.e. see an actual graph of the distribution to pick the top x percent). This may not be a problem though, we could also simply say that we pick any subreddit from, for example, the top 200 list.

Downloaded python [source code](https://github.com/subroutines/statit) for the statistics at thedonald vs enoughtrump. Looking into Praw and reddit identification.
Modified script to use my newly setup app and account. However, I sometimes get *prawcore.exceptions.ServerError: received 503 HTTP response*, which crashes the program. This happens
when the server is overloaded or something, so I will need to find an approach that can try the same request multiple times if it has failed. This is not possible with the current approach.

Had a look at [this](https://github.com/SirNeon618/SubredditAnalysis) project as well, but could not find where
the actual threads are retrieved. The rest of the code is only about the user list etc. I will likely have to
make something from 'scratch': the statitbot python code is basic enough to provide a decent start.

Statitbot outputs the csv in a very weird transposed manner, which has too many columns for the libreoffice application.
will transform the output to something different.

Using [this](https://www.reddit.com/r/funny/comments/64h1c7/the_real_way_to_eat_ramen/) post, I can find all possible
configurations of comments (i.e. comment that is a reply to a comment, comment with a URL, etc.).
It appears that whenever a link is posted in a comment, we can use body_html to search for ```<a>``` tags. Replies to a comment
are by themselves also comments, so we can check recursively.

With ```re.finditer('href="(.*)"', body)```, we can match any href (inside a comment, this should only represent linked content)
and then easily retrieve the URL using ```result.group(1)```.
We should also match the actual post using the same regexp, as (while rare) a post may be a lot of text that potentially
contains URLs. 

A problem I encountered in parsing the comments is that there may be infinitely many of them, all of which can then
have infinitely many replies. Reddit has a manual load system in place that requires the user to manually load 
more comments when there are too many. If we want to parse every single comment and reply, this will increase the complexity
of our program as well as the amount of requests we need to send to the reddit servers. The "deeper" a comment thread
gets, the less likely an individual comment is to reach the upvote threshold (which we have yet to determine). Therefore, it 
may be okay to skip these unloaded comments altogether.

I have decided to load every single comment. However, from depth 4 and onwards, we ignore every single comment
because they are very unlikely to be relevant to the main post. Furthermore, we limit the amount of parsed top-level comments
to the 2000 highest ranked comments (the *top* sorting on reddit).

The regexp returns wrong values when two links follow each other, because it tries to find the biggest possible match, taking
the begin of the first href, and the end of the second one. Therefore, we need to modify the regexp.
Found the following regexp on [stackoverflow](http://stackoverflow.com/questions/15926142/regular-expression-for-finding-href-value-of-a-a-link):
 ```
 <a\s+(?:[^>]*?\s+)?href=(["'])(.*?)\1
 ``` 
Quick testing in a sandbox environment seems to work.
 
Sometimes, the next() operation still returns a 503 error. The current way I have tried to solve this problem is by simply
trying again afterwards, but this seems to suddenly end the full loop (i.e. it says there are no more submissions to be loaded).
I will try keeping the latest processed date and time, so we can restart the full search if it crashes.

It seems to work, at least reasonably. TODO: process and filter URLs. Calculate upvote distribution. Determine fringe community or not.

### 11-4-2017
Calculated inter-reddit linkage by counting all subreddits that are not the current subreddit.
It takes roughly 45 minutes to collect 7000 URLs. Need a better way to calculate inter-linkage. 
Could reduce the sample size, but they are sorted by date, which fucks shit up.

For the upvote distribution, I will create different distributions for comments and submissions, because submissions may be more likely to gain more upvotes.

In processing soccer links, people have shared shitloads of images. These start with #, so we should filter those out.

There are A LOT of websites to blacklist. Which ones do we filter out? Are all social media (tumblr, pinterest etc.) blocked per definition? If so, is there some public blacklist
I could use?
To filter for images and videos, it may be good to check if the end of the URL is a file extension.


Called with Martin, we decided that the fringe is going to be very difficult. The approach: redditlist.com has 20 categories. Take 1-3 subreddits from each of these categories that
contains content specific to this 'niche' category. Also take top x posts from all of reddit and bottom x posts from new (i.e. all posts at least a week old, below some upvote threshold).
For each post and comment, we store the url, the amount of upvotes, the date, and the type (post or comment). For every subreddit, we store the category, the subreddit, and the date we crawled it.

Either find 5000 posts or crawl a maximum of 1 hour. 

Later process these results by calculating metrics. Metrics will depend on what people have done in existing research.
After these metrics and the filtering, we can show per subreddit a top 10 of the sites linked to.


Get all subreddits for a category from redditlist, use regexp ```/r/[^\s]* i``` to select the list of subreddits and drop all the bullshit. Then remove ```i```.
Brute forced them against each other, got list of unique subreddits per category. Some weird results:

art has /r/tf2, which is a gaming thing, but isnt actually listed in gaming.

Gaming has a very big list of unique ones, so i have decided the following: ['leagueoflegends', 'casualnintendo', 'gaming']. This is because one represents a specific game,
another a console, and the other one gaming in general. This should give maximum variety.

read and write has /r/diy, but that is bullshit. Is not related to the topic.

Having filled everything in, we have the following setup:
```` 
        'Art': ['writing', 'graphic_design', 'fountainpens'],
        'Culture': ['cyberpunk', 'opieandanthony'],
        'Discussion': ['rant', 'socialskills', 'mensrights'],
        'Gaming': ['leagueoflegends', 'casualnintendo', 'gaming'],
        'Humor': ['scenesfromahat', 'blackpeopletwitter', 'bikinibottomtwitter'],
        'Info': ['abrathatfits'],
        'Lifestyle': [],
        'Location': ['losangeles', 'croatia', 'turkey'],
        'Meta': [],
        'Movies': ['movies'],
        'Music': ['music', 'kpop', 'popheads'],
        'News And Politics': ['socialism', 'hillaryclinton'],
        'Pictures': ['perfectfit', 'highqualitygifs', 'abandonedporn'],
        'Q And A': ['iama', 'samplesize'],
        'Read And Write': [],
        'Science': [],
        'SFW Porn': ['historyporn', 'gentlemanboners', 'militaryporn'],
        'Sports': ['mma', 'eagles', 'reddevils'],
        'Technology': ['android', 'jailbreak', 'windowsphone'],
        'TV': ['strangerthings', 'community', 'rickandmorty']
````

Art has writing and fountainpens, but both of those belong to read and write more. We shift them around.
Art can then get alternativeart, which is supposed to fit under pictures.
Science is empty, so we populate it with /r/science and /r/space. Seems fine to me.

Meta literally only contains stuff that is also in another category, and is therefore not a proper category. We skip it altogether.

Filled lifestyle with fitness, makeupaddiction and relationship_advice.
Added netflixbestof to movies
Added explainlikeimfive to info


All categories now have at least 2 subreddits, and a maximum of 3.
Can now start the data gathering.

### 12-4-2017
Encountered in the morning, last 4 hours had gotten stuck. Repeatedly got 503 error, tried reconnecting for an hour.
Created new account, registered new bot, and am running from UvA IP.
Done full first level.
Second levels done: kpop, opieandanthony, croatia, eagles(half)


Kinda want to do /r/chemistry for science, to have a specific science subgroup rather than the full science.

It seems that the crawler may get stuck on the same point in multiple subreddit parsing tries. I.e. eagles got stuck 
on 2500 links, and in the second try, again on 2500 links. That's pretty weird.

Found [article](http://journals.uic.edu/ojs/index.php/fm/article/view/3498/3029) about trolls and expected behaviour in
reddit communities. Mentions the karma of the user, which indicates whether the user is likely to be a spammer or scammer.
It does give some guarantee of the popularity (=relevance?) of the content posted. However, karma works across rubreddits,
so it is not a guarantee. Unfortunately, we did not store the user or their karma, so we cant use it anyway.

[Link](http://delivery.acm.org/10.1145/2450000/2441866/p803-gilbert.pdf?ip=145.109.48.128&id=2441866&acc=ACTIVE%20SERVICE&key=0C390721DC3021FF%2E86041C471C98F6DA%2E4D4702B0C3E38B35%2E4D4702B0C3E38B35&CFID=923078645&CFTOKEN=26464083&__acm__=1492003894_ec4f5ce2ad35315841fb8aaa01bbc68e)
about websites using their users to vote and filter comment. Can maybe use their references.
Discusses  (a) subreddits, (b) linked domains and (c) types of linked content.
55% of users regularly vote posts and comments according to the article.

### 13-4-2017
Holy shit, switching the accounts actually worked. Done all them subreddits. Gonna re-do eagles and add chemistry.

For posts in new, can do something like this: https://www.reddit.com/search?sort=new&q=timestamp%3A1420070400..1420156799&restrict_sr=on&syntax=cloudsearch
Found [here](https://www.reddit.com/r/help/comments/3esyid/find_all_posts_from_one_date_within_a_subreddit/)

For posts in top, going to restrict the amount of comments per post to 1000 instead of 2000. That way, we should get more posts and not just comments.
Because the front page api doesnt inherently support a begin and end time, had to use the search query.
For both new and top, remove URL limit. Just parse for an hour. The limit is actually still used in the helper functions (parse_comment etc.), so set the limit to 100000, which
we will never reach. If we somehow magically do, that's a fine amount.

One entry in /r/mensrights was kinda malformed because the entry contained actual spaces: 

http://nzh.tw/11828283
Download the New Zealand Herald Android app here:
https://play.google.com/store/apps/details?id=com.nzherald.activities	33	1	2017-03-29 21:27:03

Just fixed it manually.

Generated graphs for the relative frequencies of different scores for both posts and comments. Display 1th to 94th percentile, 
because otherwise most of the graphs are practically empty.

New data is apparently fucked, it contains the same URLs 27 times. Need to adjust something.
Will calculate what percentile the threshold of 25 is for the_donald, and apply it to the other subreddits.
As we process the_donald anyway, I'll also use its URLs.

### 14-4-2017
Calculated threshold, and store the thresholds for each subreddit in two files for posts and comments respectively.
Also added visualisation of the threshold to each histogram.

Most post and comment distributions follow the same pattern, except:
android posts, blackpeopletwitter posts, eagles posts, iama posts, leagueoflegends posts, kpop posts, (mma posts), popheads posts, (reddevils posts),
(science posts) and top posts (obviously).

I'd like to find some way of quantitizing the distributions rather than judging them by eye. Will look for some info on distributions.

[link](http://pages.stern.nyu.edu/~adamodar/New_Home_Page/StatFile/statdistns.htm),
might be negative binomial or geometric distribution

Found python code for random samples and plot of nbinom [here](https://www.quora.com/Is-it-possible-to-do-a-probability-plot-to-see-if-a-set-of-random-data-follows-the-negative-binomial-probability-distribution)
It's not really a negative binomial, and definitely not geometric either. I do not have the time to thoroughly analyze what kind of distribution it is, nor is that part of the scope
of this project. When plotting the cumulative histogram, the odd distributions look the same as the other ones, so I assume we can just use the same way of deciding the 
threshold.

Made an overview of of top 15 posts per domain. <strong>Martin suggests extending this to 45.</strong>

Contains an error, because .co.uk is treated as a site rather than just a tld. Same for .com.tr

Adding extra overview for all of the subreddits combined.

Amount of total filtered URLs including duplicates: 52254

Without duplicates: 45112 --> These numbers have since changed, but the idea is still the same

Of the remaining filtered URLs, some seem like media, but are not necessarily. For example, wikimedia may also contain textual content. 
On the other hand, streamable.com seemed like it may contain outlinks, but it's like imgur for videos. Same for staticflickr.com, twimg.com, and
pinimg.com: they exist solely to host images.

Weirdly enough, 1 youtube link managed to get through the filtering. If you run the filter manually on that specific link, it does get blocked...


Trying to debug the new parser, found that after parsing some url that doesnt result in any urls, the last_post is apparently an empty string.
Apparently, reddit just stops giving new posts fairly quick. If you manually go to [this link](http://reddit.com/search?sort=new&q=timestamp%3A1491579242..1492184042&restrict_sr=on&syntax=cloudsearch&count=400&after=t3_65b7vn&limit=1000)
and click next a few times, you see that it quickly runs out of new pages. To circumvent this, I create a new query by using the time of the last processed 
post as an upper bound. Of course, the lower time bound is still 1 week ago. That's actually a flaw, of course the lower bound is two weeks ago, and the upper bound is 
1 week ago. Fixed it in the code.

### 15-4-2017
Still need to select those new posts below the threshold.
Done it, created final list of URLs. There are roughly 51000 of them.

Starting on scrapy, found a tutorial in combination with mongodb [here](https://realpython.com/blog/python/web-scraping-with-scrapy-and-mongodb/).


### 16-4-2017
MongoDB might be a little bit too troublesome for now. It's easy, so it's gonna work, but I'm not sure if I should spend anytime whatsoever on trying to setup a database right now.

## Week 3 
### 17-4-2017
Got a list of URLs and script codes for one website. Now need to determine when to crawl the urls, and capture the HTTP headers.
[this](https://github.com/john-kurkowski/tldextract) package should help identify whether a link belongs to the same domain.
For now, it simply crawls up to 5 external links for each starting website.

For internal links, we get an error if we link to for example index.html, or /documentation. If we want to, we'll need to prefix it with the current domain.

We now parse the response header of the manual request, but this needs to be extended to all incoming and outgoing http information, and execute javascript so that we actually
have outgoing http requests. Will look at Splash first so we have something to work with.

Splash on windows is drama, so will use ubuntu from now on. Should not be any problem as windows is generally more of a pain in the ass than ubuntu.
[This](https://blog.scrapinghub.com/2015/03/02/handling-javascript-in-scrapy-with-splash/) explains the workings of lua and splash,
can use it later to trigger events and such. 
 
### 18-4-2017
Goals for the scraping:
Get all third-party script resources (after javascript is executed)
Try to filter incoming responses on set-cookie
Maybe also try to filter the outgoing requests on sent cookies.

### 22-4-2017
TODO list:
- Split URLs on # and keep only the part before the first # (to prevent redundancy of pages)
- Find a way to detect pages that ask for a login, and skip them altogether
- Try to detect image/video file extensions on end of links so we can skip those (i.e. sstatic.net/image.png).
This may already have been done by commoncrawl.
- Check if commoncrawl respects robots.txt. If it does, we don't need to check it ourselves.

For the database and execution setup, we will use multiple SURFsara nodes. Each node will have its own crawler,
its own splash instance, and its own mongodb database. The total list of URLs to be crawled will be generated from
commoncrawl using the seed URLs. The duplicates and file extensions will be filtered out, after which the process can be
repeated if we have not reached 5 million URLs yet. This URL list will be split up over the different nodes,
maximizing the difference in domain for every node (i.e. we try avoiding crawling the same domain more than once per node).

As found on http://commoncrawl.org/big-picture/frequently-asked-questions/, commoncrawl does indeed respect
the robots.txt disallow field. Therefore, we can safely assume that we dont need to check it ourselves.

The WAT files of commoncrawl contain a list of links found on each page. For each link, they specify the type
(i.e. href, image, etc.). It looks like we should be fine if we just use the href links.

Not entirely sure how to retrieve data for specific pages, but should be some API like this:
https://github.com/ikreymer/pywb/wiki/CDX-Server-API

Maybe just use their API, or maybe use the copy at CWI/SURF.

According to [this](https://www.scrapehero.com/how-to-prevent-getting-blacklisted-while-scraping/), we may want
to set the user-agent to some browser instead of scrapy. Regarding the IP adresses, I am not certain if the different
nodes have different IP addresses. If not, we'll need to not only divide the URLs over the nodes as much as possible,
but also over time (and look at request delays etc).

It is a bit unclear what we do with websites like facebook etc. Martin suggested skipping pages with login
contents, but many websites have some kind of login form that does not necessarily impact the content (i.e. reddit).
The best option might be to simply treat them like all other websites. If there is some login wall that prevents us
from accessing the content, it will show up as isolated in the final graph (because it has no outlinks). In the manual analysis,
we will have to determine whether interesting findings are caused by blocked-off content. Mailed Hosein about this problem.

Got list of video file formats from [wikipedia](https://en.wikipedia.org/wiki/Video_file_format).
Found image formats on [here](http://www.altools.com/altools/alsee/features/view-23-image-formats.aspx).
Audio formats also from [wikipedia](https://en.wikipedia.org/wiki/Audio_file_format).

### 23-4-2017
Not sure what we do with domains like blogspot etc. where the subdomain is basically a completely different site.
Will need to ask Hosein.

It appears that some domains set multiple cookies (i.e. for independent.co.uk, pubmatic.com/ appears 14 times).
We can either remove all redundant occurrences, or we can make them unique. Depends on the clustering algorithm, so will
ask Hosein.

Also still need to ask Hosein about the ip addresses of the nodes.

To parse all scripts after the js is executed, i run a lua script with splash that executes all the js, and then
returns the HTML tree. By using this html tree instead of the default one (for a non-splash response), we get
all the scripts that are included rather than just the direct includes (so now we also see when a script loads another script).
Have tested and the 5 originally detected scripts (without splash) are also there with splash, amongst MANY others.

69+66+70+66+59+65+70+46+65+71 = 647 -> 64.7 scripts voor 0.5s

71+71+71+62+72+62+71+71+71+71 = 693 -> 69.3 scripts voor 10s

It seems that the amount of scripts found after 10 seconds is more stable than after 0.5s.
Because we should be able to run this in parallel, a waiting time of 10 seconds may not affect the performance.

Timeout of splash by default is 30 seconds. This seems fine for our purpose, because if we spend more than 30 seconds on a page,
that seems excessively long. A normal user may not even wait 30 seconds before clicking on another link.

6.61+11.15+9.18+6.8+11.10+11.73+6.36+6.01+10.96+6.92 = 86.82 -> 8.682s for executing two with 0.5s wait

15.19+14.98+19.87+16.19+16.038+16.75+11.70+11.61+15.50+17.36 = 155.188 -> 15.5s for executing two with 10s waiting time.

Thats a difference of 6.8s. During this measurement, Splash crashed once.

13.72+12.41+15.37+17.28+16.51+15.83+16.89+15.71+17.63+16.47 = 157.82 -> 15.78 for three sites and 10s waiting time.
Thats an increase of 0.18s for an extra website.
10 seconds is the maximum allowed value of wait, so we'll have to go with that.
All time was measured between the start of the start_request function and the end of the last parse function.

This means we now have a final script to run on all websites. The lua script disables images and enables plugins,
so cookies can be set through flash etc.


Commands: 
```
docker run -p 8050:8050 scrapinghub/splash --disable-ui
sudo service mongodb start
```

## Week 4
### 24-4-2017
Will look into this splash crash today. Seems a GTK issue, ran apt-get update and upgrade,
and installed libgtk-3-0 and libgtk-3-common, and -dev and -bin.

Enabled autothrottle with a delay between 5 and 60 seconds. Set concurrent requests per domain to 1 to 
prevent being blocked by the server.

Changed list of test websites to an old alexa 500, because my own samples from reddit contain a lot of nonexistent
pages. Got list from Mees' github, asked him where they're from.

Added retry middleware to retry on 400 response. Retries 2 times.

The splash errors:
```
(python3:1): Gtk-CRITICAL **: IA__gtk_widget_get_visual: assertion 'GTK_IS_WIDGET (widget)' failed

(python3:1): Gdk-CRITICAL **: IA__gdk_colormap_new: assertion 'GDK_IS_VISUAL (visual)' failed

(python3:1): Gdk-CRITICAL **: IA__gdk_colormap_alloc_colors: assertion 'GDK_IS_COLORMAP (colormap)' failed

(python3:1): Gtk-CRITICAL **: IA__gtk_widget_modify_bg: assertion 'GTK_IS_WIDGET (widget)' failed

```
The actual crash with increased verbosity:
```
1   0x7fd481db1ee7 /opt/qt55/lib/libQt5WebKit.so.5(WTFCrash+0x17) [0x7fd481db1ee7]
2   0x7fd481df77f5 /opt/qt55/lib/libQt5WebKit.so.5(_ZN3WTF11OSAllocator6commitEPvmbb+0x35) [0x7fd481df77f5]
3   0x7fd481ddecdd /opt/qt55/lib/libQt5WebKit.so.5(_ZN3WTF21PageAllocationAligned8allocateEmmNS_11OSAllocator5UsageEb+0x7d) [0x7fd481ddecdd]
4   0x7fd481ae2905 /opt/qt55/lib/libQt5WebKit.so.5(+0x1679905) [0x7fd481ae2905]
5   0x7fd481ae2119 /opt/qt55/lib/libQt5WebKit.so.5(+0x1679119) [0x7fd481ae2119]
6   0x7fd481ae287b /opt/qt55/lib/libQt5WebKit.so.5(_ZN3JSC15MarkedAllocator16allocateSlowCaseEm+0x11b) [0x7fd481ae287b]
7   0x7fd481c13907 /opt/qt55/lib/libQt5WebKit.so.5(+0x17aa907) [0x7fd481c13907]
8   0x7fd43b11f08d [0x7fd43b11f08d]

```
Somebody has [the same](https://github.com/scrapinghub/splash/issues/467) issue.

#### The cluster
Installed python on the cluster using anaconda. Using conda, created a python3.5 environment that
I will use to install the necessary packages. So far, I have installed all python packages I need, 
and have installed mongodb. 
The environment is activated with:
```
source activate ~/env/
```

Mongo is run with the following command: 
```
mongod --dbpath ~/mongodb/db/
```
I now need to install splash for everything to work. This will have to be without docker, as that is 
not allowed (cant install without sudo).

Splash needs [re2 library](https://github.com/google/re2/) and gives the following error:
```
    gcc -pthread -Wsign-compare -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes -fPIC -I/home/hazarbon/env/include/python3.6m -c src/re2.cpp -o build/temp.linux-x86_64-3.6/src/re2.o
    cc1plus: warning: command line option '-Wstrict-prototypes' is valid for C/ObjC but not for C++ [enabled by default]
    src/re2.cpp:249:29: fatal error: re2/stringpiece.h: No such file or directory
    compilation terminated.
    error: command 'gcc' failed with exit status 1

```
Will try installing it manually, as it otherwise requires sudo.
Joke is on me though, because it also requires sudo when installing manually.
Ran make install on the source above, gives 
```
mkdir -p /usr/local/include/re2 /usr/local/lib/pkgconfig
mkdir: cannot create directory `/usr/local/include': Permission denied
mkdir: cannot create directory `/usr/local/lib/pkgconfig': Permission denied
```

This all goes wrong because scrapy tries to (pip) install the python re2 library. This requires the
re2 linux package, which requires sudo access. I think running ```sudo pip install -r requirements.txt```
inside ~/splash would fix the problems.


Tried [pyv8](https://code.google.com/archive/p/pyv8/) library, also requires sudo.

And [SpiderMonkey](https://github.com/davisp/python-spidermonkey), also requires sudo.

Tried JS2PY, but will crash on stuff like window, document.body etc.

On https://wordpress.com/, phantomjs detects 18 scripts and 0 cookies. Splash found 0 scripts and 13 cookies.
On https://www.nytimes.com/, phantomjs found 56 scripts and 0 cookies. Splash found 49 scripts and 9 cookies.
However, phantomjs did find a huge collection of first-party cookies.

For https://soundcloud.com/, phantomjs found 10 scripts and 0 cookies. Splash found 10 scripts and 9 cookies.
For independent.co.uk, 66 scripts, 0 cookies. Splash 62 scripts, 49 cookies.

Conclusion:
phantomjs is slow (not parallel), and cannot find third-party cookies. For scripts, however, it works fine.
http://stackoverflow.com/questions/17146514/how-to-get-3rd-party-cookies somebody has the same problem.

Selenium timeout is not working on the cluster. The timeout is there, but is way too high (i.e. 1 second 
is more like 5 seconds).

http://phantomjs.org/api/webpage/handler/on-resource-received.html

### 25-4-2017
Running both splash and phantomjs on the first 10 websites of alexa500.
Phantomjs: 30.22 + 23.39 + 27.59 + 23.60 + 23.34 + 19.53 + 15.72 + 14.41 + 15.83 + 24.02 = 217.65 -> 21.7s
splash: 13.99 + 13.42 + 

First 100:
splash: 106.51 -> 1.06s
phantomjs: 317.11 -> 3.17s

All 500:
phantomjs on cluster: 1026.82, 1404.947, 215.82 ->  2647.587s total, avg. 5.295s
phantomjs local: 3004.50, 726.783, 325.598 -> 4056.88s total, avg 8.11s
Both locally and on the cluster, roughly 15-20 websites took too long to process.

Setting user agent to Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0


Strangely, on local i get this error:
```
Could not get response from http://liveinternet.ru
```
After which all subsequent websites raise
```
[Errno 111] Connection refused
```



Installed brew on server
http://blog.teamtreehouse.com/install-node-js-npm-linux
https://github.com/NiklasGollenstede/get-tld
Might be able to pull this off and get the cookies as well, but is highly likely to be very very slow.
When installing node, many dependencies fail. However, when i install them manually, it seems to work.
Concurrent phantomjs page loading: https://github.com/ariya/phantomjs/issues/11408

Called with Maarten, decided that we will try to get an admin run the commands. If not at SURF, maybe ILPS.

For the Node approach, I could not use the get-tld library. Therefore, I reduce all urls to their domains, 
including their subdomains. A cookie from the same top-level domain, but a different subdomain, will then
be regarded as a third-party cookie.

Tried running node crawler on first 50 of alexa. Weirdly, phantomjs crashes with a segmentation fault whenever
you try to measure the elapsed time. Will try calling the script on one website at a time via python.

According to [SURF userinfo](https://userinfo.surfsara.nl/systems/lisa/usage/batch-usage#heading6), no job can run
for more than 120 hours. Having set the original schedule on two weeks, that means we'll have to use more 
nodes. It is probably best to split it up in two parts. Small tutorial on batch systems: https://userinfo.surfsara.nl/systems/shared/batch-howto

To run many jobs at once:
```
qsub -t 1-100 myjob
```
Will launch 100 identical copies of the jobscript 'myjob'. Since these are all identical, 
you should take care that each job 'knows' what to do. You could use the environment variable 
PBS_ARRAYID, which contains the number of the job:
```
  #PBS -lnodes=1:cores16:ppn=16 -lwalltime=1:00:00
  cd $workdir
  module load openmpi
  echo starting working on problem $PBS_ARRAYID
  mpiexec ./my-parallel-program $PBS_ARRAYID
  echo ended working on problem $PBS_ARRAYID
```
Maybe instead of two parts, just split it up in 14 parts of 1 day each?

Have made a multi-threaded python script that calls the phantomjs script for 1 url per thread.
##### Local
Execution times on first 10 alexa:
9.473 + 9.30 + 5.32 + 6.74 + 5.18 + 5.403 + 8.29 + 5.586 + 5.31 + 4.896 = 65.49 -> 6.5s avg.

Single phantomjs script call running on 10 sites at a time:
9.80 + 6.43 + 5.08 + 6.92 + 5.849 + 5.12 + 5.67 + 5.59 + 5.42 + 9.054 = 64.93 -> 6.5s avg.

Therefore, there is no notable difference between these approaches.


NOTE: Need to correct source (and possibly cookie) URLS. For example, a script can have source = /source_file.js
This needs to be changed to http://www.domain.ext/source_file.js. Also need to change // to http://, etc.

Mongo couldn't connect at first, but apparently it works if you run the server as a daemon. Use the following command:
```
mongod --dbpath ~/mongodb/db/ --fork --logpath ~/mongodb/log/mongod.log
```
Probably have to use shutdownserver command now: 
https://docs.mongodb.com/manual/tutorial/manage-mongodb-processes/#start-mongod-as-a-daemon

Ran the phantom node script, gives following error:
```
TypeError: null is not an object (evaluating 'c.classList')

  https://static.licdn.com/scds/concat/common/js?h=3kp2aedn5pmamdr4dk4n8atur-3ti5bgrnb6idjtk0w4chaigxe-5hqr1i1uoezoj0z1s5gcxojf2-71o37tcjwl0ishto9izvyml3i-3bbdjshpw5ov0rwa8xe08tp97-cayct4cirf7n0f9z1xsg84g0q-dktkawxk7k8pixuh5g8z5ku32-213zbp2wzp99lviwl8g2cvq6i-1lknwtftishpdmobzm413yc7u-bcxa0v9ke411pjpmz4s239f9b-10wg3j2jlwnawjalr4lur4ho3-82rcsw42m1wbgsti4m3j0kvg6-f3la2n4kbk7vr56j54qax1oif-1eq1il9757v2zkuru6hu14q2e-8sox1gztdjnz2un89fi8fyw35-8hdbl769kuhp0h4bsexhsbks0-c6ct0moql4p4ngtzltmf8l3ly-7raunjy3cqumnf5qbuxliw2nh-2s77lcl0ztx2c5fzyqvglptj1-bn7x20my6ejwhlgl10oqmhgst-8h514j3fiwnzuwkt66sbxsu8f-di2z9sra5co9la7ogqyesywin:71 in h
  https://static.licdn.com/scds/concat/common/js?h=3kp2aedn5pmamdr4dk4n8atur-3ti5bgrnb6idjtk0w4chaigxe-5hqr1i1uoezoj0z1s5gcxojf2-71o37tcjwl0ishto9izvyml3i-3bbdjshpw5ov0rwa8xe08tp97-cayct4cirf7n0f9z1xsg84g0q-dktkawxk7k8pixuh5g8z5ku32-213zbp2wzp99lviwl8g2cvq6i-1lknwtftishpdmobzm413yc7u-bcxa0v9ke411pjpmz4s239f9b-10wg3j2jlwnawjalr4lur4ho3-82rcsw42m1wbgsti4m3j0kvg6-f3la2n4kbk7vr56j54qax1oif-1eq1il9757v2zkuru6hu14q2e-8sox1gztdjnz2un89fi8fyw35-8hdbl769kuhp0h4bsexhsbks0-c6ct0moql4p4ngtzltmf8l3ly-7raunjy3cqumnf5qbuxliw2nh-2s77lcl0ztx2c5fzyqvglptj1-bn7x20my6ejwhlgl10oqmhgst-8h514j3fiwnzuwkt66sbxsu8f-di2z9sra5co9la7ogqyesywin:71
  https://static.licdn.com/scds/concat/common/js?h=3kp2aedn5pmamdr4dk4n8atur-3ti5bgrnb6idjtk0w4chaigxe-5hqr1i1uoezoj0z1s5gcxojf2-71o37tcjwl0ishto9izvyml3i-3bbdjshpw5ov0rwa8xe08tp97-cayct4cirf7n0f9z1xsg84g0q-dktkawxk7k8pixuh5g8z5ku32-213zbp2wzp99lviwl8g2cvq6i-1lknwtftishpdmobzm413yc7u-bcxa0v9ke411pjpmz4s239f9b-10wg3j2jlwnawjalr4lur4ho3-82rcsw42m1wbgsti4m3j0kvg6-f3la2n4kbk7vr56j54qax1oif-1eq1il9757v2zkuru6hu14q2e-8sox1gztdjnz2un89fi8fyw35-8hdbl769kuhp0h4bsexhsbks0-c6ct0moql4p4ngtzltmf8l3ly-7raunjy3cqumnf5qbuxliw2nh-2s77lcl0ztx2c5fzyqvglptj1-bn7x20my6ejwhlgl10oqmhgst-8h514j3fiwnzuwkt66sbxsu8f-di2z9sra5co9la7ogqyesywin:71
  https://static.licdn.com/scds/concat/common/js?h=3kp2aedn5pmamdr4dk4n8atur-3ti5bgrnb6idjtk0w4chaigxe-5hqr1i1uoezoj0z1s5gcxojf2-71o37tcjwl0ishto9izvyml3i-3bbdjshpw5ov0rwa8xe08tp97-cayct4cirf7n0f9z1xsg84g0q-dktkawxk7k8pixuh5g8z5ku32-213zbp2wzp99lviwl8g2cvq6i-1lknwtftishpdmobzm413yc7u-bcxa0v9ke411pjpmz4s239f9b-10wg3j2jlwnawjalr4lur4ho3-82rcsw42m1wbgsti4m3j0kvg6-f3la2n4kbk7vr56j54qax1oif-1eq1il9757v2zkuru6hu14q2e-8sox1gztdjnz2un89fi8fyw35-8hdbl769kuhp0h4bsexhsbks0-c6ct0moql4p4ngtzltmf8l3ly-7raunjy3cqumnf5qbuxliw2nh-2s77lcl0ztx2c5fzyqvglptj1-bn7x20my6ejwhlgl10oqmhgst-8h514j3fiwnzuwkt66sbxsu8f-di2z9sra5co9la7ogqyesywin:71

```
After this, the output is normal.

It seems to crash on linkedin, as these are linkedin scripts.


### 26-04-2017
Tried pip install scrapy. Running the server raises an error about glibc, about which some wisdom  can be found
[here](http://stackoverflow.com/questions/37525884/importerror-lib-libc-so-6-version-glibc-2-14-not-found-required-by-usr-li).

Tried manual install, but glibc 2.14 is not compatible with the gcc version brew installs (5.3). The install
files advise gcc 4.1. Trying gcc4.6, as that is the oldest version brew can install. 
Brew won't properly install it, so tried manual install of 4.1. Raises an error saying that makeinfo is missing,
so tried building gnumake. Raises the following error:
```
make[2]: Leaving directory `/home/hazarbon/packages'
make[1]: Leaving directory `/home/hazarbon/packages'
```
Which is completely useless... Is probably because I did not put the directory inside some new build directory.
Trying that now with texinfo, it is in ~/packages/build-texinfo/texinfo-6.3.
It actually worked, added texinfo to path. Now gonna retry building gcc.

Building gcc also results in an error, but it seems to be due to its source code:
```
.././gcc-4.1.0/gcc/toplev.c: At top level:
.././gcc-4.1.0/gcc/toplev.c:524:1: error: redefinition of 'floor_log2'
 floor_log2 (unsigned HOST_WIDE_INT x)
 ^
In file included from .././gcc-4.1.0/gcc/toplev.c:59:0:
.././gcc-4.1.0/gcc/toplev.h:175:1: note: previous definition of 'floor_log2' was here
 floor_log2 (unsigned HOST_WIDE_INT x)
 ^
.././gcc-4.1.0/gcc/toplev.c:559:1: error: redefinition of 'exact_log2'
 exact_log2 (unsigned HOST_WIDE_INT x)
 ^
In file included from .././gcc-4.1.0/gcc/toplev.c:59:0:
.././gcc-4.1.0/gcc/toplev.h:181:1: note: previous definition of 'exact_log2' was here
 exact_log2 (unsigned HOST_WIDE_INT x)
 ^
make[2]: *** [Makefile:2060: toplev.o] Error 1
make[2]: Leaving directory '/home/hazarbon/packages/gcc-build/gcc'
make[1]: *** [Makefile:4166: all-gcc] Error 2
make[1]: Leaving directory '/home/hazarbon/packages/gcc-build'
make: *** [Makefile:618: all] Error 2
```
Error is the same as [here](https://bugzilla.redhat.com/show_bug.cgi?id=476370), but that is regarding running
the compiler on actual code, not the installation of the compiler itself. [same](http://stackoverflow.com/questions/34569458/error-occurred-compiling-gcc-from-source-code)
error, but this time on the actual building. It turns out that I can edit the makefile to add the flags that are suggested: -fgnu89-inline

Turns out i'm missing/messed up another package: libc-dev. I think this is actually the glibc-2.14 i was trying to install
before. Anyway, [this](https://askubuntu.com/questions/251978/cannot-find-crti-o-no-such-file-or-directory) might work, so
i'll give it a try (configure with --disable-multilib). Gives an error once again: 
```
Configuring in ./fixincludes
configure: loading cache ./config.cache
configure: error: `CC' has changed since the previous run:
configure:   former value:  gcc
configure:   current value: gcc -fgnu89-inline
configure: error: changes in the environment can compromise the build
configure: error: run `make distclean' and/or `rm ./config.cache' and start over
make[1]: *** [Makefile:3727: configure-fixincludes] Error 1
make[1]: Leaving directory '/home/hazarbon/packages/gcc-build'
make: *** [Makefile:618: all] Error 2
```
Which means we're pretty much going in circles here. WIll try one other version of gcc (3.4.6), then give up.
It leads to the same error as before, so I suppose that's the end of splash on the surfsara cluster.

One more try of http://splash.readthedocs.io/en/stable/install.html:
pip install -r requirements.txt needs the re2 package. Will [build manually](https://github.com/google/re2).
Make ran successfully. Make test as well, make install gets permission error. -> NVM, installed with brew.
Still some errors, looking into pyre2. Doesnt work either, edited makefile of re2 to have a prefix in the current
folder (~/packages/re2/installed-re2). This should prevent any permission errors.
Because re2 is local, had to manually install and change pyre2 as well, but i succeeded.

##### After installing splash succesfully. I get the same error as when installed with pip if i try
##### to run it. This is officially the end of splash on surfsara. I give up.

### 28-04-2017
Error in phantomjs seems to be internal. It happens between calling page.open() and the first line 
of the open function, and cannot be caught by a try catch. It does not break the program though, so hopefully
we can just split stdout from stderr.

Turns out there is actually an onError function in phantomjs that captures error in javascript execution.
It correctly catches this specific error, there is probably just bad javascript code on the crawled page.

It is still weird that the javascript only causes errors when executed on the server, but that is probably due
to differences in javascript versions or something.

Now that it works, I can try executing many of them. Made a jobscript to execute a single one,
but it works using the pbs array index thing, so we should be able to call multiple at a time.
Trying to execute it with
```
qsub -t 0-2 ~/Node-Phantom/jobscript -lnodes=1:cores16:ppn=15 -lwalltime=00:03:00
```

The script fails to output the files if we are in the Node-Phantom folder (due to the dash in its name probably).
Works fine if executed from home folder. Changed the command above.

Job outputs (not the data, just the output of the bash scripts) for running the above command:
```
Starting program at 28-04-2017 14:09:11
ID: 0
Program finished at 28-04-2017 14:09:18
Elapsed time: 7 seconds

Starting program at 28-04-2017 14:10:03
ID: 1
Program finished at 28-04-2017 14:10:10
Elapsed time: 7 seconds

Starting program at 28-04-2017 14:10:54
ID: 2
Program finished at 28-04-2017 14:11:01
Elapsed time: 7 seconds
```

It can be seen that they did not run in parallel, and have therefore in this case not gained us any
time efficiency. This is likely because they are all separate jobs, so each of them has a different priority.
Because all of them are very small jobs (10 websites each), this scheduling overhead really slows down the process.
I will create 1 job that launches multiple processes to gain more control over the execution times of each process.


Even then, it seems difficult to properly parallelize everything (I get some bash errors, but perhaps the biggest flaw
is in my thinking). To properly keep track of when processes are done (so that we may launch new ones and not 
waste our cores), it is probably best to launch a python script that will then spawn multiple processes.
Will look into the multiprocessing library now.

https://userinfo.surfsara.nl/systems/lisa/filesystems provides info about using the scratch filesystem.

If we process all of alexa 500 with 30 processes, that means 17 websites per process. 
If we take an average of 7 seconds per site, that would take 119 seconds. Therefore, we can test it with
a walltime of 3 minutes, that should be enough to parse all and get performance measures.

Running 15 processes on half of the set, this is the output:
```
Starting at 28-04-2017 15:59:46
Process 8 took 10.441282272338867 seconds to complete.
Process 2 took 10.641836643218994 seconds to complete.
Process 3 took 10.694981098175049 seconds to complete.
Process 1 took 10.735204219818115 seconds to complete.
Process 6 took 10.862365245819092 seconds to complete.
Process 4 took 10.926037549972534 seconds to complete.
Process 7 took 10.955925703048706 seconds to complete.
Process 5 took 11.050196170806885 seconds to complete.
Process 12 took 11.476887941360474 seconds to complete.
Process 10 took 11.493487119674683 seconds to complete.
Process 14 took 11.777445793151855 seconds to complete.
Process 9 took 13.679552555084229 seconds to complete.
Process 13 took 13.760296821594238 seconds to complete.
Process 11 took 14.6846182346344 seconds to complete.
Process 0 took 15.552451372146606 seconds to complete.
Program finished at 28-04-2017 16:00:02
Elapsed time: 16 seconds
```
That's a total of 178.73, meaning an average of 11.92s per process. As each has parsed 17 websites, 
that would mean an average of 0.70s per website. This seems weird given the fact that we calculated
roughly 6s before.

Lets run 15 processes on the total set. That means 34 websites per process.
This is the output:
```
Starting at 28-04-2017 16:10:04
Process 13 took 6.2187440395355225 seconds to complete.
Process 1 took 11.77754259109497 seconds to complete.
Process 2 took 11.776412010192871 seconds to complete.
Process 4 took 12.004667282104492 seconds to complete.
Process 3 took 12.116016864776611 seconds to complete.
Process 12 took 13.024243831634521 seconds to complete.
Process 9 took 13.798445463180542 seconds to complete.
Process 11 took 23.94069790840149 seconds to complete.
Process 8 took 26.70641803741455 seconds to complete.
Process 10 took 27.95341920852661 seconds to complete.
Process 5 took 66.47344493865967 seconds to complete.
Process 6 took 67.1986711025238 seconds to complete.
Process 7 took 69.06969022750854 seconds to complete.
Process 0 took 96.1801187992096 seconds to complete.
Process 14 took 98.66356754302979 seconds to complete.
Program finished at 28-04-2017 16:11:43
Elapsed time: 99 seconds
```
That's an average of 37.126s per process, meaning an average of 1.091s per website. This seems
fair enough, because we only tested half of the websites before, and some are slower than others.

However, when looking at the actual output data, all processes have crashed, and none of them have
output any data.

Interesting stuff: http://stackoverflow.com/questions/9961254/how-to-manage-a-pool-of-phantomjs-instances
Somebody made a multi-process phantomjs node library. Might be useful and could replace the python script 
altogether. 

To try and fix the error, will run a few of these manually:
```
executing command: phantomjs /home/hazarbon/Node-Phantom/crawler.js 0 34
executing command: phantomjs /home/hazarbon/Node-Phantom/crawler.js 34 34
executing command: phantomjs /home/hazarbon/Node-Phantom/crawler.js 68 34
executing command: phantomjs /home/hazarbon/Node-Phantom/crawler.js 102 34
executing command: phantomjs /home/hazarbon/Node-Phantom/crawler.js 136 34
executing command: phantomjs /home/hazarbon/Node-Phantom/crawler.js 170 34
executing command: phantomjs /home/hazarbon/Node-Phantom/crawler.js 204 34
executing command: phantomjs /home/hazarbon/Node-Phantom/crawler.js 238 34
executing command: phantomjs /home/hazarbon/Node-Phantom/crawler.js 272 34
executing command: phantomjs /home/hazarbon/Node-Phantom/crawler.js 306 34
executing command: phantomjs /home/hazarbon/Node-Phantom/crawler.js 340 34
executing command: phantomjs /home/hazarbon/Node-Phantom/crawler.js 374 34
executing command: phantomjs /home/hazarbon/Node-Phantom/crawler.js 408 34
executing command: phantomjs /home/hazarbon/Node-Phantom/crawler.js 442 34
executing command: phantomjs /home/hazarbon/Node-Phantom/crawler.js 476 34
```
It seems to go wrong when there are too many websites parsed at the same time (i.e. 30 is too many).
It gives a segmentation fault, probably because it runs out of memory or things start to overlap or 
something. If this is the case, it would be fairly easy to fix by setting a smaller batch size, so instead
of running 1 process on 34 websites, we run 3 subsequent processes on 10 each.

Implementing this in python (signalling when processes are done, etc) seems to be an unnecessary amount
of work, so will look at the phantomjs-pool library first. This also has built-in support for segfaults,
auto-restarts etc., so looks promising.

Should note that the default worker timeout is 2 mins, so if i decide to do a few websites in batch,
this might affect results.

Running the full 500 on the cluster:
Elapsed time: 907 seconds. -> 1.8s average per website, which is pretty good!
For some reason, the output.json is fucked up though. Only contains the first 3 websites or so. Will 
have to look into this.

Set timeout to 10s, because it misbehaves on the cluster. We need 30s, but setting it to 30s would even
allow 60s. I hope 10s should more closely approach 30s.

Turns out the above result were using 4 workers instead of 15, because i forgot to update a parameter.
In theory this means that we can gain a lot of speed improvement, so that's exciting news.
Results of 15 processes:
```
Total time:  2531.670999999999
Average time:  5.053235528942114
Program finished at 28-04-2017 19:14:30
Elapsed time: 190 seconds
```
Given this total time of 190s per 500 websites per node, that's an average of 0.38s per website for 1 node.
That means that if we'd run this for 5 days straight, we should be able to get 1136842 websites. Running
multiple nodes and/or iterations of this, we should be able to reach 5 million in the two weeks given for
execution. 

TODO for this weekend:
- count the occurrence of the same script/cookie source and add in a dictionary instead of a list
with duplicate entries -> decided that we do this afterwards (but probably still on the cluster)
- strip cookie/script urls from query parameters etc.
- calculate in/outbound links for each url
- prepare presentation

### 29-04-2017
There are some sneaky script urls like 
```
https://www.gstatic.com/og/_/js/k=og.og2.en_US.bL-0WKDKItk.O/rt=j/m=def/exm=in,fot/d=1/ed=1/rs=AA2YrTsZP5CqGqH6-rrNeALehxWbBEeE3g
```
That make it very difficult to strip the query part of the url. For the above example, i would need to look up
the closest / to the left of the first = and strip everything from there onwards. That will become too much
effort for such an operation. Will have to determine what to do with this.

There is also this case: 
```     
https://x.bidswitch.net/ul_cb/sync_a9/https%3A%2F%2Fs.amazon-adsystem.com%2Fecm3%3Fex%3Dbidswitch.com%26id%3D%24%7BUUID%7D
```
in which i'm not sure whether we should split on the %. I think it may be used for webpages as well, for example
news pages with titles that contain a space.

Results on cluster with the url correcting in place:
```
Program has finished successfully.
Total time:  4896.787000000003
Average time:  9.774025948103798
Program finished at 29-04-2017 19:33:20
Elapsed time: 403 seconds
```
The amount of time has been doubled. That seems very wrong.
Also, I currently remove the www. but not the scheme. It seems to me that for the clustering, http or https
will not be relevant, so we should probably leave it out. Judging from these performance estimations though,
it is probably best to not filter the URLs at all, and maybe do it afterwards if we have some efficient
way to check them.

Am now running a test to measure the time without the URL correction algorithm to see if this is
indeed the reason that everything is suddenly very slow. Result:
```
Program has finished successfully.
Total time:  2278.325
Average time:  4.54755489021956
Program finished at 29-04-2017 19:54:34
Elapsed time: 208 seconds
```
That's more like the 190 we had before. The average time is even lower. Let's now test with some
indexOf methods rather than split functions in the extractDomain function. According to 
[this](https://jsperf.com/slice-vs-substr-vs-substring-vs-split-vs-regexp/2), it should be faster.
Old function:
```
function extractHostname(url) {
    var hostname;
    //find & remove protocol (http, ftp, etc.) and get the hostname
    if (url.indexOf("://") > -1) {
        hostname = url.split('/')[2];
    }
    else {
        hostname = url.split('/')[0];
    }

    var www = hostname.split('www.');
    if(www.length > 1){
        hostname = www[1];
    }

    //find & remove port number
    hostname = hostname.split(':')[0];

    return hostname;
}
```
New function:
```
function extractHostname(url) {
    var hostname = '';
    //find & remove protocol (http, ftp, etc.) and get the hostname
    var schemeIdx = url.indexOf("://");
    if (schemeIdx > -1) {
        hostname = url.substring(schemeIdx + 3);
    }

    var slash = hostname.indexOf('/');
    if(slash > 0){
        hostname = hostname.substring(0, slash);
    }

    var www = hostname.indexOf('www.');
    if(www > -1){
        hostname = hostname.substring(www + 4);
    }

    //find & remove port number
    var port = hostname.indexOf(':');
    if(port > -1){
        hostname = hostname.substring(0, port);
    }
    return hostname;
}
```
Results:
```
Program has finished successfully.
Total time:  2297.280000000001
Average time:  4.5853892215568886
Program finished at 29-04-2017 20:27:53
Elapsed time: 177 seconds
```
Does not seem to make any notable difference, which seems fairly weird. However, we do have to
take into account that this is just one performance estimation, and the real way to test these
is to just run them on a list of strings.

Have now set page.settings.loadImages to false. Will include hyperlink detection and do another 
performance estimation:
```
Program has finished successfully.
Total time:  1916.1619999999994
Average time:  3.8246746506986016
Program finished at 29-04-2017 20:55:05
Elapsed time: 155 seconds
```
The hyperlink detection has probably slowed it down, but disabling the images has led to a
significant speed increase. Great results!

Out of the 500 crawled website, only 1 has returned 'undefined', meaning it took longer than
30 seconds to process the website.

Will now split on the '?' and ';', just because it shouldn't affect performance too much, but does save 
a lot of (visual) space in the output.

Performance:
```
Program has finished successfully.
Total time:  1802.9310000000019
Average time:  3.5986646706586862
Program finished at 29-04-2017 21:18:45
Elapsed time: 134 seconds
```
That's even better than the last time. Of course the performance is slightly random, but this does
indicate that we do not lose any significant performance. 
The output file is only 350kb instead of the regular 900kb. This should be because of the removed,
unnecessary query parameters, but just to be sure, let's run the same script again:
```
Program has finished successfully.
Total time:  1600.6580000000008
Average time:  3.1949261477045923
Program finished at 29-04-2017 21:27:23
Elapsed time: 150 seconds
```
Once again, only 350kb. Results seem fine, don't think anything is missing.
Then, let's also strip the scheme and trailing slash.
```
Program has finished successfully.
Total time:  1800.7179999999985
Average time:  3.594247504990017
Program finished at 29-04-2017 21:54:28
Elapsed time: 150 seconds
```
Performance still fine, file has shrunk to 300kb. All good. It was probably slow
before because I used a substring to check somewhere, rather than indexof.
Because the function is called so many times, that would slow things down, although i didn't
expect it to double the time needed per website.

Will run one final test to confirm that we can use this script as is:
```
Program has finished successfully.
Total time:  1513.6609999999987
Average time:  3.0212794411177617
Program finished at 29-04-2017 22:06:13
Elapsed time: 111 seconds
```
Absolutely ridiculous. The performance keeps magically increasing. 
Output file still 300kb, results are looking good.

As we'll parse the urls once more after the crawl to count their occurrence, we can also
filter out some of those that are from the same domain (but different subdomain) by stripping 
on slash and then comparing domains. 
For example if the main domain is tumblr.com, and a script is from img.tumblr.com, we will be
able to filter it out. Of course this doesn't capture all of them, but it should clean up the
data a bit more.

## Week 5
### 01-04-2017
Looking into commoncrawl API today. Turns out the API is only for retrieving the indexes (where the 
data is stored), not the actual data itself. Can be accessed for 'free' with amazon AWS service, meaning
I would have to pay only for the usage of the clusters etc, not the access to the crawl data.

Mailed Hosein about this (getting access to the local copy at surfsara), and will in the meantime write
a script that retrieves all the indexes for us.

Found ujson library, which should be faster than normal python json. If necessary, we could use this
in retrieving the indexes.

Wrote a python script, takes 7 seconds to get the index information of 100 websites. Thats 0.07 per 
website, so that would take 2800 seconds for 40000 websites. I'll divide it up into 4 parts of max 15 mins each.

Of the first 100 urls, none are in the commoncrawl data. Probably because they are more recent than the
latest commoncrawl version. While waiting for a confirmation of this, I will research ways to use the urls
that are produced by the crawler, so we don't process anything beforehand. This will require some mechanism
to prevent URLs from being visited multiple times, server overload etc.

I just realised that we did not split the scheme from the filtered URL list. While this is good because
it ensures that the URL will be correct (for example, some websites might require us to use https, and if
we strip the scheme, it might not work correctly), it introduces a possibility for the same URL to be
present in the list twice. We'll have to check the urls of the two schemes against each other to prevent this.
Or maybe we don't, because we remove the duplicates later anyway.

From the seed URLs: part 4 has 2575 results. Part 1 has 2924, Part 2 has 2996, part 3 has 1937.
That's a total of 10432 out of 41927 seeds URLs.

After doing some research into recursive crawling, I have concluded that it isn't worth it. 
As I wrote in an email to Hosein:
<div style="font-style: italic;">
I now have 1 master process and 15 worker processes. The master process has the full list of URLs, and whenever a worker process is done crawling a specific url, the master will assign it a new one. 
To implement recursive crawling, the starting list would contain our 40000 seed urls. All of these are crawled in order, and together with the results we store in the output file, every worker returns a list of outbound links found on the page as well. We'd have to keep one list (FIFO) for all the urls that are in the queue, and one list for all visited URLs. Furthermore, we'd need to keep a dictionary of the amount of urls we have visited per domain, so we can check that it remains below 1000. Then, when a worker is done with a certain url, we can assign it a new one from the queue immediately, and then start processing the found URLs, checking all of them against both the domain counter and all previously visited links (which will be max. 5 million). 
It would probably be most efficient to run the string comparisons in a separate thread, so the master process isn't blocked. It takes an average of about 3.5 seconds to crawl a webpage, so the time spent on adding a new URL to the queue (or not) should be at most 3.5/15 = 0.23s to ensure that we always have URLs in the queue. This doesn't seem absurdly low, so we might be able to pull it off (but do take into account that we also need to strip the URL of query parameters, filter URLs with media file extensions, etc.). In any case, it will mean that we can run one less process per node.

The huge downside of this, however, is that it only works on one node at a time. I plan to run at least two nodes simultaneously, and even if we are able to share information between the nodes, that would double the amount of work for the string comparison thread. It is probably possible to sacrifice more cores for more administrative power, but that will greatly increase the complexity of the code I will have to write, as well as significantly impact the performance.
</div>

I even forgot to mention in this email the problem of dividing up the workload over time to prevent
us from overloading any servers. This would require so much complexity and overhead that it seems
more sensible to choose Common Crawl, even if that does limit us to less than 5 million URLS because of
the time it takes to look up the indices.

### 02-05-2017
The URL collector is done way quicker than I thought it would, took maybe 12 hours to parse all
the subreddits. Only need to do top and new.

New parser got stuck after 6500 URLs, so just stopped it manually. Apparently, I overloaded the server and got
blocked. Will need to do top later.

Tried the new URLs on the indexer; 22 out of 100 URLs were found in commoncrawl.
Therefore, I think the total amount will still be roughly 10000 out of 40000, but we'll see.

Top is too difficult to parse, because it sorts on upvotes and not on time. Therefore,
I cannot use the same approach as with the new query (which search within a specific timespan),
and the normal approach won't work either, because it will take the top posts as they are today.

Will try the indices with the new values for all subreddits and new, but with the old top posts.
Also used old values for the donald, because the threshold of 25 is arbitrary anyway, and it is not part of 
our set of subreddits, so it was not parsed again.

Results: 3312 + 3508 + 2250 + 3010 = 12080 out of approx. 41000 URLs. That's more than we had previously,
but the difference isn't significant, taking into account the possibility of duplicate URLs with a different
scheme. It is probably best to use the old urls from the original reddit crawl, so all the data is coherent.

http://stackoverflow.com/questions/30304719/javascript-fastest-way-to-remove-object-from-array
Is about fastest way of removing object from array. Apparently fastest to remove property from object,
so that's what we'll do.

Current approach of URL sorting doesn't seem to work; there are approximately 27000 unique URLs, and
555 for the domain imdb.com. That means there should be roughly 48 urls in between each occurrence of
an imdb url, but there are roughly 20 in between the occurrences. Furthermore, it takes a long time (
I estimate around a minute) to order the list of just 30000 URLs. That will take way too long
for 5 million URLs if we don't parallelize this. Will not further look into this
right now, because it seems likely that we won't be able to use the Common Crawl anyway.

https://wiki.mozilla.org/TLD_List
This may be useful if I decide to implement a domain check rather than a subdomain check.
```javascript
var test = "/setprefs?suggon=2&prev=https://www.google.nl/?gfe_rd%3Dcr%26ei%3D8LsIWdjHFqak8wfewaaIBg%26gws_rd%3Dssl&sig=0_V5l-NI5n4OGHVwSptEOx_3JcI0I%3D";
console.log(extractHostname(test));
```
Outputs google.nl. That is a flaw, because it detects the https in the query arguments. Will fix it by splitting
on the / first, and the scheme later. <- that doesn't work, because it will detect the / in the ://.

Found https://www.npmjs.com/package/parse-domain, which seems to work. Will save a LOT of effort.
Will run it on the old worker to see the performance impact. Output:
```text
Program has finished successfully.
Total time:  3560.259999999999
Average time:  7.106307385229538
Program finished at 02-05-2017 20:03:40
Elapsed time: 321 seconds
```
That's drastically lower than 3.5s and 111 seconds. Will run another test without the package
to confirm that this is the reason:
```text
Program has finished successfully.
Total time:  1748.9960000000012
Average time:  3.4910099800399226
Program finished at 02-05-2017 20:09:37
Elapsed time: 135 seconds
```
Indeed, this package considerably slows us down.

Changed //*/@href to //a/@href, so we don't include script tags etc., just hyperlinks.

Running performance measurement on the recursive crawler. As of now, it simply checks each incoming
URL against the queue and the finished URLs. It does not use the domain package, nor does it count URLs
per domain or prevent server overload. Result:
```text
Program has finished successfully.
Total time:  2039.6010000000012
Average time:  4.071059880239523
Program finished at 02-05-2017 20:30:46
Elapsed time: 691 seconds
```
That's pretty bad. That's 1.382 seconds per website for a whole cluster. That means we'd be
able to crawl 313000 websites for 5 full days on one node. We can still use another node, but 

Weirdly, though, it has not added any items to the queue. There must be something wrong with the code.
Found the bug and fixed it. Was just some string comparison problem. Will re-run the recursive crawler
with the processLinks disabled. That should have the same performance as the original crawler,
because we do not actually do anything new outside this function.

Also running the original master locally, so I can compare the results with the cluster (to check
if any IP filtering occurs). 

Forgot switching numWorkers to 15 instead of 3, so that's why the non-processing master was slow.
Will have to re-run both the non-processing master and the recursive master again with 15 workers.

non-processing:
```text
Program has finished successfully.
Total time:  1585.8230000000005
Average time:  3.165315369261478
Program finished at 02-05-2017 21:02:35
Elapsed time: 115 seconds
```

processing:
```text
Program has finished successfully.
Total time:  1706.2650000000008
Average time:  0.09778583299902578
Program finished at 02-05-2017 21:07:10
Elapsed time: 153 seconds
```
This is nice! 153 is perfectly fine! The average is fucked because the queue contains all newly added
items in it as well, so the total is going to be way higher than the processed 500.

Replaced time measure per worker with time spent on processing: 
```text
Program has finished successfully.
Total time spent on processing:  2.0269999999999935
Average time spent on processing:  0.003943579766536952
Program finished at 02-05-2017 21:24:16
Elapsed time: 149 seconds
```

Also rerunning the domain name package, may have been the wrong amount of workers as well.
```text
Program has finished successfully.
Total time spent on processing:  0.43200000000000033
Average time spent on processing:  0.0008404669260700396
Program finished at 02-05-2017 21:36:39
Elapsed time: 280 seconds
```
That's way better than the 700 we had before, but still almost double the time. May be worth it though,
will have to see after implementing the domain filter etc. It may even be more efficient in the end,
because the amount of domains will drastically decrease. Therefore, we have to check less domains
per URL. Could also do it just on the master side, and keep the old approach on the worker.

Added mini-optimization for filetype checking (if there is no dot, there cant be an 
extension). Results:
```
Program has finished successfully.
Total queue length: 17228
Total time spent on processing:  2.7219999999999898
Average time spent on processing:  0.005295719844357957
Program finished at 02-05-2017 22:10:54
Elapsed time: 127 seconds
```
Seems to actually have increased the processing time, so will remove this "optimization".
Is probably because charAt is slower than the array matching or something.

For some reason, using processLinks and the domain stuff calls the same worker on the same index
twice (or maybe it just returns twice). Maybe because computations take too long? Could do them
on a separate thread, will need to look into NodeJS multiprocessing. --> Apparently it just returns 
twice. The worker is only called once. Only the print is executed twice, the processLinks isnt. This
is because one of the results is undefined. Setting spawnWorkerDelay does not affect the problem.
-> This randomly seems to have fixed itself.

Have implemented the domain check. Performance:
```text
Program has finished successfully.
Total queue length: 13319
Total time spent on processing:  1.516999999999998
Average time spent on processing:  0.002951361867704276
Program finished at 02-05-2017 22:48:55
Elapsed time: 131 seconds
```
Weirdly, the processing time has gone down, along with the total queue length. No domain has 
reached the limit, however, so that is not the reason. Will need to check the actual output
file json tomorrow.

### 03-05-2017
The output seems fine. 383kb is around the usual size, and the contents of the file look fine too.

Was a flaw in the code in which it did not add the first URL of every domain.
Fixed it, new results:
```
Program has finished successfully.
Total queue length: 17624
Total time spent on processing:  3.3159999999999896
Average time spent on processing:  0.00645136186770426
Program finished at 03-05-2017 13:30:20
Elapsed time: 132 seconds
```
This seems more realistic. Time on processing has gone up, but total time hasn't really.
Thats good.

Running another (unaltered) test with 20 processes to see if it speeds things up further.
With ```#PBS -lnodes=1:cores16 -lwalltime=00:15:00```:
```text
Total queue length: 17490
Total time spent on processing:  3.0729999999999915
Average time spent on processing:  0.005921001926782257
Program finished at 03-05-2017 14:22:31
Elapsed time: 146 seconds
```
That's slower than before, so we'll stick to 15.

NOTE: may have to replace // with http:// for all links found in recursive, depending on how phantomJS
handles them. -> don't bother, just skip. 

Maybe good for a quick little research:
look at the most popular filetypes of each media type, and sort them in order. That might optimize
a tiny little bit.

For some reason, recursiveMasterOld (getting recursive links from 4 URLs without any cooldown checker)
does not add new items to the queue (or it does not process them).

Will have to fix this so I can compare the performance result with the cooldown check.
Problem is fixed. Result for recursiveMasterOld:
```text
Total queue length: 3274
Total time spent on processing:  0.27700000000000014
Average time spent on processing:  0.0005389105058365762
Program finished at 03-05-2017 19:05:49
Elapsed time: 134 seconds
```

Result for the cooldown implementation:
```text
Total queue length: 4571
Total time spent on processing:  0.4190000000000003
Average time spent on processing:  0.0008151750972762652
Program finished at 03-05-2017 19:34:42
Elapsed time: 75 seconds
```
That's really weird; elapsed time has almost halved. None of the domains had reached the cooldown
limit, so that doesn't explain anything. Will manually check the output file.
Apart from the occasional //link returning 0 for every entry, everything looks fine. Really strange.

Caught 404 errors so we don't output them to file anymore.
Made an extra output file, data.json, which holds the unprocessed queue, allUrls, index, etc.
We can use this to start a new crawl after finishing one.

Only thing left is intermediate copying from scratch to home, but do not know how to do that
(except via a separate python script or something, but that seems shit).

Crawler now stops on a time limit rather than an URL limit. Have loaded in all seed URLs, and hope
to run an hour long test tonight.

Program timer is an hour, SURFsara walltime is 1.5h. Should be fine.
Results:
```text
Program has finished successfully.
Total queue length: 165231
Total crawled URLs: 16164
Total 404 errors received: 2198
Total time spent on processing:  270.46499999999537
Average time spent on processing:  0.016732553823310774
Program finished at 03-05-2017 22:51:10
Elapsed time: 3609 seconds
```
That's 0.22s per website. That's even less than I expected!
The data file is 27MB and the output file is 19MB. So 46MB for 16164 URLs -> 2.8KB per URL.
For 5 Million, that will be roughly 14GB. Nothing we can't handle!

Will now run it for 5 hours to see what happens. Walltime 6.5h.

NOTE: loading in the data file (to continue where we left) could theoretically happen in parallel.
We'll probably have to, with these sizes.

### 04-05-2017
Had a meeting with Jeroen Schot from SURFsara to get access to their hadoop cluster and the Common Crawl
dataset. We could use it, but processing it would be a fairly complex and intensive process (either we have
to spend time sending many requests to the API or we have to spend time manually finding all our URLs
in the dataset, which is multiple terabytes).

It seems that the recursive crawler is fairly quick, so it's likely better to use it for both the
data collection and the URL gathering process. After we have reached 5 million, we can skip all the 
administrative tasks of the crawler (except the server overload prevention) and run it on the list
we have created. We'll already have processed the first part of the (seed) URLs, and saved the results,
so we do not lose any data.

Even without the save function, the program does not seem to stop after 5 hours. This might be 
because of some bug in checking the amount of finished workers. What I'll do instead is finish the
program 30 seconds after the first worker is done (so when the time is up).
Have canceled the 5 hours one, had also crawled about 80000 URLs after 7 hours. 
This hints even more in the direction that our crawl was probably done, but the finish function was never called.

Have restructured data (queue, domains, etc) into several CSV (tab separated) files, rather than 1 big JSON file.
This should help with reading them in parallel.  Now save hyperlinks as part of the data as well.
Will run a test for 3 hours, just to see if everything behaves correctly. In the meantime, I will
transform the output from a JSON file into a bytes file so that we can also later parse them
in parallel.

Will also have to look at parsing robots.txt and the lost file issue (if we crash or run out of
 time).

Found [this](https://www.npmjs.com/package/robots-txt-parser) for robots.txt; will have to measure its performance.
Doesn't really work, does not work in worker thread, so has to be in master, and then the aSync functions
are broken (callback is never called). Calling sync in the master would fuck our efficiency straight up
the ass, so that's not gonna happen. Will look for something else.

https://github.com/ekalinin/robots.js/tree/master seems to work,
so will now run performance estimation with recursiveMasterOld (so we can compare it to
previous results on alexa 500).
```text
Total queue length: 3364
Total time spent on processing:  0.2990000000000001
Average time spent on processing:  0.0005817120622568095
Program finished at 04-05-2017 20:07:42
Elapsed time: 146 seconds
```
It seems that robots.txt does not considerably slows us down! That's great.

Results of earlier 3 hour crawl:
```text
Total crawled URLs: 51548
Total 404 errors received: 6351
Average time spent on processing:  0.04973494606968192
Total time spent on processing:  2563.7369999999637
Total queue length: 464980
Program finished at 04-05-2017 20:03:40
Elapsed time: 10835 seconds
```
It has exited normally after the 3 hours, taking 35 seconds to produce the data files.
The average time per website is still around 0.22s, which is good.
It has gained a total of 464980 - 51548 = 413432 new queue URLs for 51548 crawled URLs. 
That's 8 new URLs per crawled URL, so if we'd use this just for URL collection, we'd still need to crawl
to crawl 625K seed URLs.

| File name | size |
| :---:       | :---:  |
| all_urls.csv | 20MB |
| domains.csv | 4.8MB |
| output_file.json | - |
| queue.csv | 31MB |

Only the output file is ridiculously small for some reason (307KB). Definitely something wrong there.
I already know what's wrong: both the big crawl and the smaller 500 were in the queue at the same time.
The smaller job has overwritten the bigger ones. That's really annoying.

We have 194229 domains for these 464980 URLs. I estimated roughly a quarter of the URLs to be
a new domain before, but it's already 0.41 now. Don't know if this will hold, but that would mean
roughly 2 million domains (and thus nodes in the graph) for 5 million URLs.

File size of 1KB per URL probably won't hold, because we already have 1.2KB now, excluding the output
file. Previously, the output was roughly a third of the data output file, so let us expect another
0.4KB for the data. This isn't a problem, because that's still only 8GB of data for 5 million URLs.
Even if we store all data twice, which we eventually do, that is all very manageable.

Still store the output as JSON, but it is no longer a list, just a sequence of objects. For every object,
its offset is stored in offsets.csv. The size can be calculated by looking at the next offset.

I have now also implemented the robots.txt check in the regular recursive crawler.
 The results are depressing:
```text
Total crawled URLs: 15
Total 404 errors received: 5
Average time spent on processing:  0.009733333333333333
Total time spent on processing:  0.146
Total queue length: 41977
URLs skipped because of robots.txt: 26
```
More URLs have been skipped than they have been crawled. And of those crawled, 5 returned 404 and 3
returned undefined, meaning we only have 7 results. Will try changing the user agent and see what happens.

NOTE: should test the new jobscript first for a minute or so to confirm that it works correctly.

TODO TOMORROW: 
- Do partial output file copy instead of just copying the full file [x]
- check test of testjob, adapt where necessary [x]
- measure ratios and performance with everything enabled for at least an hour. 
For this test, use the tld library. Have to specify output folder in command line now.[-]

### 05-05-2017
After running for roughly a minute, the highest offset in the file is already 296463, and this is
just the 54th URL (which is actually strange, because that would mean an average of 5.4KB per URL
and we calculated roughly 1KB before). If we have 5 million URLs, we'll have 27,450,277,777 bytes.
This is just over the max integer limit (for 32-bit integers). Luckily, according to [this](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/MAX_SAFE_INTEGER),
the max number is actually 9,007,199,254,740,991 , because JavaScript doesn't actually use integers.
It uses Numbers, which are some kind of double precision numbers with a max of 2^53 or so. 

Mailed to Maarten about respecting robots.txt, and he says we probably have to ignore the robots.txt.
Otherwise, websites with "shady constructions" might easily avoid showing up in our results. Furthermore,
it would be interesting to log whether a site has robots.txt, so we can analyze if there tends to be
a difference between tracking code on sites with robots.txt and those without.

Will enable correctURL, because we get fairly many undefined and 404 results (around 12%). Hopefully, this will
improve the success rate.

Now logging the robots.txt block rather than respecting it. Changed robots user agent back to '*'.

File copying with the new folder system etc. seems to work. Just need to pass the output folder
to the master via command line args so we can copy the intermediate files to the same directory
as well.

Partial file copy is working fine, the total of all partial files is exactly as much as the total.

There seems to be an error in the robots.txt parsing. Looking at [this tester](https://en.onpage.org/free-tools/robots-txt/?refresh=1&url=http%3A%2F%2F100photos.time.com%2Fphotos%2Fpeter-leibing-leap-into-freedon&useragent=Googlebot&submit=Evaluate),
it says we should be allowed. However, my output data says we aren't. Will have to look into this.
If I extract all "forbidden" URLs from the output, and try them again, all of them are allowed.

The problem might be caused by the callback functions. When the robots.txt is tested, it is
 actually a different URL than the one we set it to (i.e. the next one).
 
Apparently, the robots library wants us to point to robots.txt manually, and then check a specific
URL. I guess we can try http://domain/robots.txt? 
 
Have tried with https://registreermijnmerk.nl, because I know they have a robots.txt file.
Even though it is https, taking its domain (registreermijnmerk.nl) prefixed with 'http://' and
suffixed with '/robots.txt' seems to work perfectly.

New data for 72 seconds of local crawling:
```text
Total crawled URLs: 42
Total 404 errors received: 7
Average time spent on processing:  0.023547619047619053
Total time spent on processing:  0.9890000000000002
Total queue length: 42140
Disrespected robots.txt files: 23
```
The actual amount of output objects is 32, so 3 URLs have for some reason returned undefined.
Will look into this now.
http://7.62x54r.net/mosinid/mosinm38.htm returns undefined, but is actually a 404.

When the worker returns undefined, the page.open is never actually triggered. For simplicity,
I will assume that this means a 404 in all cases.

One more local test:
```text
Total crawled URLs: 41
Total 404 errors received: 9
Average time spent on processing:  0.017219512195121956
Total time spent on processing:  0.7060000000000002
Total queue length: 42140
Disrespected robots.txt files: 23
```
This should then mean that we have 32 websites in our output file, and indeed it does. Perfect.

Will now try it on the cluster for a few minutes, and then I can later try it for roughly
3 hours to make an estimation of the amount of data we can get in 5 days.

Results for 72 seconds:
```text
Total crawled URLs: 253
Total 404 errors received: 32
Average time spent on processing:  0.006616600790513828
Total time spent on processing:  1.6739999999999986
Total queue length: 43556
Disrespected robots.txt files: 129
----------------------------------
Program finished at 05-05-2017 16:23:53
Elapsed time: 103 seconds
```
Not all workers have been closed, which means they were shut down at the 30 seconds finish 
timeout. Therefore, we can subtract 30 seconds from the total, leaving us with 73 seconds for 253
websites. That's 0.29s per website, which isn't too bad compared to the 0.22 we had before,
considering that we now use the slower domain extraction library.

We have 221 output entries, which is in correspondence with 32 404 errors. 
It seems that correcting the URLs hasn't really made a difference to the amount
of 404 errors. It is still 12%.

The summed size of the partial outputs is roughly 3KB less than the total file, which is fine because
the copying happens on an interval, so of course we won't have all the data.

Reading the data out works fine. 580KB total output, which means roughly 2.6KB per URL.
Will do proper estimations after a longer run of 3 hours. The job has been submitted to the queue
at 16:37.
Results:
```text
Total crawled URLs: 16442
Total 404 errors received: 2492
Average time spent on processing:  0.009078092689453884
Total time spent on processing:  149.26200000000077
Total queue length: 108484
Disrespected robots.txt files: 5520
----------------------------------
Program finished at 05-05-2017 19:38:53
Elapsed time: 10832 seconds
```
That's an average of 0.66s per website, which is a bit unfortunate, because it means only 650K URLs after 5 days.
We can probably restart it afterwards for another run, but we're not likely to do more than two in total, optimistically bringing
us to 1.3M URLs. 15% of those will be 404, so we'll have data from around 1.1M URLs. While not as much as I might have hoped, it will suffice.

| File name | size now | expected size for 5M | expected size for 650K|
| --------- | -------- | -------------        | ----------------------|
|all_urls.csv| 5.5MB   | 1.672GB | 217MB |
|domains.csv| 464KB    | 141.1MB | 18MB  |
|offsets.csv| 122KB    | 37.1MB  | 4.8MB |
|output     | 54.6MB   | 16.6GB  | 2.1GB |
|queue.csv  | 7.2MB    | 2.19GB   | 284MB |
| total     | ~70MB	   |  ~20GB   | ~2.6GB|

Files stored in 
/home/jelmer/Cluster/1493995101.

Will queue the full crawl now.

### 06-05-2017
Program has crashed.... 
```
Results:
Program finished at 06-05-2017 07:38:33
Elapsed time: 26252 seconds
```
It seems to have done 46393 websites. That is 0.56s per website, which is pretty nice.
However, this is just the index, so there are probably still some websites in the queue.
Might still be 0.66s.


The error log:
```
events.js:163
      throw er; // Unhandled 'error' event
      ^

Error: read ECONNRESET
    at exports._errnoException (util.js:1050:11)
    at Pipe.onread (net.js:581:26)
```

Might be node port issue?

http://stackoverflow.com/questions/17245881/node-js-econnreset

Put uncaughtexception handler in master (worker doesn't recognize it because it is
PhantomJS rather than NodeJS)
Need to work on the restart mechanism ASAP so I can restart the process if it crashes.

Added this:
http://phantomjs.org/api/webpage/method/close.html

Because I get a lot of memory errors every time I launch now...
Added flag --max_old_space_size=8192 to increase node memory. Don't think it will
affect anything right now, but it might prevent a crash when we near the end of the time
limit.

## Week 6
### 08-05-2017
It's still going, so I hope the problem has been fixed.

### 09-05-2017
Now going for 62 hours, seems to be going fine. Will look into the graph algorithms etc. 
today. Hosein suggested Louvain modularity, so will look into that.

Louvain Modularity runs in O(n log n). 
https://en.wikipedia.org/wiki/Louvain_Modularity
[Paper](https://arxiv.org/pdf/0803.0476v2.pdf) about Louvain detection shows that it
outperforms other algorithms significantly on required time. They show an example of
a phone network with 2.6M nodes and 6.3M edges, on which they reach a modularity of 0.769
in only 134s. That is really quick. 

NOTE: the higher the modularity, the better defined the communities are. Modularity is
a value between -1 and 1. Louvain (and other clustering algorithms) tries to optimize 
this value.

NOTE from the paper:
One should also note that the output of the algorithm depends on the order in which
the nodes are considered. Preliminary results on several test cases seem to indicate that
the ordering of the nodes does not have a significant influence on the modularity that
is obtained. However the ordering can influence the computation time. The problem of
choosing an order is thus worth studying since it could give good heuristics to enhance
the computation time.

[This](https://github.com/Sotera/distributed-louvain-modularity) is a distributed implementation
of Louvain, but it requires Hadoop. Cannot find whether the original authors used a 
distributed implementation. Will try a 'regular' implementation first.
- [Nodejs package for Louvain](https://www.npmjs.com/package/ngraph.louvain)
- [Python package for Louvain](https://pypi.python.org/pypi/louvain/)

[Comparison of community detection algorithms](https://arxiv.org/pdf/0908.1062.pdf) seems
to show that Louvain? (blondel et al) is a well performing algorithm. It's a really
unclear article, so can't really conclude anything without reading it thoroughly.

The paper about louvain does not mention anything about directed or undirected graphs,
but ours will be directed. [This paper](https://hal.archives-ouvertes.fr/hal-01231784/document) shows that we can use
it anyway, and the accuracy might be even better than an undirected graph.

Creating the hyperlinking graph is fairly straightforward. The only thing I'm not yet 
certain of is whether I need to normalize the weights (probably, I do). However, if I do,
this needs to happen afterwards anyway, so that isn't a problem right now.

What to do with the tracking code presents a bigger issue. As I've sent in an email to
Hosein:
```text
The question then is how to do the same with the cookie and script domains. I'm still
not entirely clear on what my specific goal is. I could try to find a community of
websites (a silo) and then determine if I can find any patterns in the tracking code 
used on these websites (i.e. because they are inside a specific cluster, does that mean 
they are likely to use the same tracking code?). Would that even require a graph for 
the tracking code, or do I simply look at the output communities of the algorithm, 
and then do some simple statistics on the code found on these pages?

Another approach would be creating a separate graph for the tracking code, that links 
the code hosts to the websites they are used on. I can then, completely separate from 
the hyperlinking information, link pages together because they use the same tracking 
code. However, creating such a graph is way more complex than creating a hyperlinking 
graph. For each website, I would have to compare the tracking code used with that on 
every single other website in the data, and somehow determine whether they are similar 
enough (i.e. defining some similarity threshold). Honestly, I have no idea how to 
realise this graph. I could also simply created a weighted edge from each website to 
each tracking code host, and then run Louvain on it, but because the tracking code 
hosts will only have incoming edges, and no outbound connections, I'm not sure 
if this would be considered a community by the algorithm. If it is, then that would
be a more interesting result (comparing the two community graphs) than simply looking 
at the tracking code used in the found communities.
```

For now, I'll just start on a hyperlinking graph. I think the most sensible approach
for the above issue is to just try Louvain on it (if this does not take too long), and
see if it results in any useful communities. If it doesn't, I could resort to just doing
the simple analytics.

I'll also need to calculate some metrics for this graph, for which I'll look at the 
paper Martin has suggested me before (disrupting criminal networks). It may be that we
can compute these metrics during the graph creation.

I'll create this graph in python, because the python package for Louvain seems more promising
than the NodeJS one. Also, I [should be able](http://stackoverflow.com/questions/35936991/how-to-create-gephi-network-graphs-from-python
) to use python to visualise stuff in Gephi.

[iGraph tutorial](http://igraph.org/python/doc/tutorial/tutorial.html) for creating a graph
in python. Should be able to use weights with 
```
G.es['weight'] = [1.0, 3.0, 5.0]
```
This example will set the weights of the three edges to the respective values.

Because I will do my analysis on a domain basis, I'll need to group all the websites by their
domains before I can create a linkage graph between these domains. I'll use pymongo to fill
a MongoDB.

The python [fileinput library](https://docs.python.org/3/library/fileinput.html) is
very useful. Can read across multiple files, return cumulative lineno, etc.

There seems to be a bug in the offset file, sometimes an offset is missing.
That is very annoying. It most likely happens because of an error in the writing.
No idea why this error would occur though. 203 out of 5797 return an error (because
the chunk size is incorrect).
Weirdly, all the written data is completely correct (there are no partial JSON objects).
Even more weirdly, the next offset is also correct, and contains the full object of which
part is in the erroneous area. Therefore, I assume my file is correct, but the read
operation is somehow reading too much.

It doesn't go wrong with only 1 process, so it seems there is something wrong with the
paralellization. Probably the seek function is overlapping or something.
-> It does go wrong with only 1 process, just not in the example I was looking at before.

It also happens that an offset is listed twice.
Using only 1 process, all errors contain exactly two fully correct objects (so we are missing)
one offset, that seems fair enough because it could happen on a write error.

It seems that every time there is an error, it occurs when an offset is listed twice.
I think I have found the cause of the bug: the callback uses the global variable as 
output variable. Because it is a callback, the variable might have changed in the meantime.
Therefore, we log the same offset twice, essentially deleting one of our entries.
I did take this in mind with the copy function, but not with the actual write function.
I might have fixed the problem now, but I'm not certain. It might be possible that it 
still occurs, because the second write could be performed in between the first write and
the increasing of the counter. However, my javascript knowledge is not sufficient to 
confirm whether this is true.

It seems that opening the file separately in each process removes part of the problem.
There are no longer partial JSON objects, I just have to deal with the double situation.
Turns out we only lose 22 out of 5797, rather than 203. That's not too many, so for now,
I'll just skip the erroneous objects.

Uploaded the data into a domains collection in mongodb. There are apparently 2258 domains,
which seems correct. To ensure that it is, will need to run through the db and count the 
URLs.

TODO tomorrow:
- Count URLs in database [x]
- (optional) Read all output files, not just one
- Create graph (try the different approaches) [/]
- Run Louvain on said graph

### 10-05-2017
Counted URLs, and the amount is correct.
Created graph based on just the hyperlinking, and pickle the results so I can easily process
them. Takes roughly 1 minute for just 1 output file (meaning 120 minutes for a full job).

Installed gephi so I can try to visualise the data. The visualization is fairly pointless,
it is just one big interconnected mess.

Can't install igraph on the cluster because of glibc2.14 (once again, goddammit).
Will have to find another way to do it (maybe NodeJS after all).

### 11-05-2017
Found new python louvain package: https://github.com/taynaud/python-louvain.
Uses networkx instead of igraph, so hope I can install that on the cluster.
-> Successfully installed.

The detection algorithm takes an optional parameter scale, of which I can't find out
what exactly it means. 

With networkx, I can use any object as a node (i.e. the full domain object). However,
since its functions are very similar to igraph, I will just keep the index dictionary
for now and store them as numbers.

[Networkx docs](http://networkx.readthedocs.io/en/networkx-1.11/tutorial/tutorial.html)

Not sure if the algorithm works with directed graph, so may have to use the convert 
function to convert it to undirected.

Networkx has built-in functions to export to certain file formats, some of which 
are supported by Gephi. Therefore, I can discard my original, manual conversion script.

It also has drawing functions that draw the graph to pyplot. Should look into
the different ways of visualizing the results.

Building the graph seems to be WAY faster than igraph, which is great.

Can change size and color of nodes and edges in gephi based on different attributes
(i.e. degree). That is useful for visualization. Only need to find out how to get the
name of each node.

Can already see that facebook and twitter have a very high degree, much of which is inbound.
Other websites of interest are blogspot and google, of which blogspot has many outbound links
and google is neutral. 

The community package does indeed not support directed graphs.
Will try converting it by simply adding upthe weights in both directions.

After running the community detection, it has found 172 nodes out of the 10000 websites
present in total. Seems good. However, it is apparently a random process (probably because the
graph is essentially a dictionary, and dictionaries are unsorted), so the amount differs
each time. Could maybe prevent this by using sorted graph (have not looked at it), but
does not seem an issue for now.

Will try to list the websites inside each cluster.

There are some very big clusters; there is one with only porn websites (which is good,
because those should belong to the same community) that contains like 50 or 80 websites.
Some news websites also seem to be grouped together.

For some reason, every community contains a link to itself. Don't think that matters though.

Will now try integrating the cookie and script information.

Not yet filtering stuff like jquery and captchas, I get some unexpected results.
The community that previously (almost)only contained porn websites, now has a lot
of new non-porn members. They do not seem related, so maybe something interesting is
happening, but likely they just use the same advert networks or something.

The crawler has done the first part completely. This is the output log:
```text
Time is up, closing worker 4 at Thu May 11 2017 15:01:26 GMT+0200 (CEST)
Finishing program in 30 seconds from now
DONE: 485020
Time is up, closing worker 8 at Thu May 11 2017 15:01:27 GMT+0200 (CEST)
Thu May 11 2017 15:01:34 GMT+0200 (CEST): Successfully copied output to home directory
null
Thu May 11 2017 15:01:34 GMT+0200 (CEST): Successfully copied offsets to home directory
DONE: 484962
DONE: 484969
Time is up, closing worker 8 at Thu May 11 2017 15:01:36 GMT+0200 (CEST)
Time is up, closing worker 4 at Thu May 11 2017 15:01:36 GMT+0200 (CEST)
DONE: 484976
Time is up, closing worker 8 at Thu May 11 2017 15:01:36 GMT+0200 (CEST)
DONE: 483960
Time is up, closing worker 4 at Thu May 11 2017 15:01:51 GMT+0200 (CEST)
----------------------------------
Finishing program, saving output data
Total crawled URLs: 490821
Total 404 errors received: 135139
Average time spent on processing:  0.05394547095582037
Total time spent on processing:  26477.570000006708
Total queue length: 1098807
Disrespected robots.txt files: 128886
----------------------------------
Writing timeQueue to file
Writing uncrawled queue to file
Writing allUrls to file
Writing domain counters to file
Program has finished successfully.
  notice: Q: "...sara_stats": -------------------Begin of SURFsara epilogue----------------------------------
Q: "...sara_stats": This output was generated by the SURFsara epilogue script
Q: "...sara_stats": Your job [final_crawl_1] has been executed in queue [serial] with
Q: "...sara_stats": the following PBS arguments:
Q: "...sara_stats":    ncpus=1,neednodes=1:cores16,nodes=1:cores16,walltime=120:00:00
Q: "...sara_stats":    .
Q: "...sara_stats": Resources used in job [511736.batch1.lisa.surfsara.nl] with name [final_crawl_1]:
Q: "...sara_stats":    cput=225:36:56,energy_used=0,mem=33043320kb,vmem=269733516kb,walltime=120:00:58
Q: "...sara_stats":    r10n16.lisa.surfsara.nl
Q: "...sara_stats":    .
Q: "...sara_stats": Job start and end time:
Q: "...sara_stats":   Job start time: Sat May  6 16:01:23 CEST 2017
Q: "...sara_stats":   Job end time  : Thu May 11 16:02:26 CEST 2017
Q: "...sara_stats": ---------------------End of SURFsara epilogue----------------------------------
```
Unfortunately, for some reason I can't explain, the program finished successfully, but never exited,
therefore not causing the bash script to move on to the copy operations. The solution for
this is simple: I should have copied the files as part of the finishProgram function rather
than handle it in the bash script. Furthermore, I could have also set a copyinterval for
the queue and allUrls. The domains would always get lost, but we could easily (albeit fairly
slowly) reconstruct them from the URL lists. These are all easy solutions in hindsight,
but they won't get me anywhere now. Luckily, I still have all data from this job because of
the intermediate copies, but I won't be able to restart and continue the crawler.

### 12-05-2017
Will import all the output data into the database. I have merged all output files into
one big single file. Weirdly, when I process all of the offsets on this big file,
only 4857 entries are processed. The process function is called 355K times, but each of
the individual processes has only parsed roughly 1700 URLs. Maybe the main process quits
while the children are still working? -> This is indeed the reason.

Even pool.close() was not enough, so now keep a list of processing results (boolean).
By iterating this list and waiting for all entries to complete, I can both verify that
all processes have finished and count the amount of objects we store in the database.

Have locally imported all data:
```text
processed 350843 objects
All data has been imported. Took 4851.164121627808 seconds.
```
There are 83657 domains.

#### Hyperlink graph
Creating a graph and writing it to file takes only 56 seconds locally.
The graph file is only 72MB. Will try opening it in gephi.
Gephi crashes because it has run out of memory. Can try allocating more RAM to it 
somehow. 

According to gephi, there are 256137 nodes and 823496 edges.
Using 6GB of RAM, it is able to visualise this, although it is painstakingly slow.

Measurements for creating the hyperlink community graph:
```text
Reading in graph file.
Done, took 58.77263069152832 seconds.
Converting to undirectional graph
Done, took 4.260481834411621 seconds.
Running Louvain algorithm
Done, took 39.4059796333313 seconds.
Writing community graph to file
Done, took 1.2124319076538086 seconds.
Total elapsed time: 103.6516923904419 seconds.
```
The graph contains 879 nodes and 6001 edges.

#### Total graph
Measurements for creating total graph:
```text
Collecting all nodes and edges
Done, took 51.14010000228882 seconds
Constructing graph from data
Done, took 8.220196962356567 seconds
Writing output file
Done, took 17.875144243240356 seconds
Total elapsed time: 77.2365391254425 seconds
```
The graph is 160MB.

Converting it to community graph:
```text
Reading in graph file.
Done, took 126.87703323364258 seconds.
Converting to undirectional graph
Done, took 10.13350224494934 seconds.
Running Louvain algorithm
Done, took 94.86187934875488 seconds.
Writing community graph to file
Done, took 2.9362809658050537 seconds.
Total elapsed time: 236.64723539352417 seconds.
```

Have also created script for on the server, which should be a bit faster.
I have a jobscript that copies the merged_output to its local storage, then starts
a mongodb server, imports all the files, and then dumps the database and copies the
files back to /home/hazarbon.

Server script has been killed after running for two hours, which is strange.
It might be that the bottlenecking (see explanation at the bottom of this doc) has
caused it to be that slow, but I think there is just a mistake somewhere.
Anyway, it did not take extremely long to import everything locally, so I won't bother
fixing the problem. Can always upload the database to the cluster.
Not sure how much data we have lost because of the race conditions, so should ideally
fix the problem some time.

Have written some Node data recovery scripts to reconstruct the queue, domain counter 
etc. from the database. When this is done, I can restart the crawler. It takes a while
to compute everything, but that's not really a problem right now. Will be a few hours 
at most.

Should first run allUrls.js, and then generateQueue.js.

It stopped after 43000 domains, but it should have done all 83000. This happened because 
I set the time to 20 seconds, and the time required increases exponentially (we have to
match more and more strings). Will make it a counter of the exact amount of domains(83657).
These callbacks are a bit annoying to work with.

Made an adapter crawler to later use the recovered URLs. Removed all URL checking mechanisms,
so is no longer recursive. The recovery is now at 69000 out of 83000 domains, and already
takes a few minutes for every 1000 domains, so the checking mechanism is definitely
slowing down the crawler significantly. I think that if I still use the mechanism,
I wouldnt even be able to crawl 500K urls in 5 days. Without it, I should manage to 
crawl the complete list.

Speed measure (on my laptop):
```text
73000->74000 = 4min
74->75 = 4min
75->76 = 5.5min
76->77 = 4.33min
77->78 = 3.25min
78->79 = 1.5min
79->80 = 2. 17min
80->81 = 7.5min
81->82 = 5.5min
82->83 = 5min
```
Quickly estimating the average, thats 5 mins per 1000 domains. Idk how many URLS are in those domains, but i could have a look.
Then I can estimate the required processing time. It may not actually be too bad, but I'll still remove the whole queue system from
the crawler. We'll have done 2 complete crawls, and I do not mean to start a third one anyway. If anyone desires to continue the crawler,
they can use the recovery scripts I have written.

This points out something I already knew: this is not an efficient system. It seems
that for 500K or more target URLs, it would be worth to set up some hashing mechanisms
and a B+ tree or something to speed up the comparison process.

Am now uploading the data files to google drive, so I can retry loading in the database
on my desktop PC with the new mechanism to see what's wrong. In the meantime, my
laptop is still running the recovery scripts.

For some reason, importing is way faster on my laptop. It takes roughly 10 seconds
per 1000 URLs, compared to 30 seconds on my desktop. Wtf? My desktop has a better processor.

All data has been imported. Took 9311.599953651428 seconds.
Somehow, the queue only contains roughly 300K URLs. I expected it to be 500K, and then
possibly another 135K for all 404 errors.

### 13-05-2017
Although the queue is surprisingly small, have started the second crawl on it now.

Will now run the graph algorithms on the newly imported dataset to see if there are 
any obvious differences.

The hyperlinking graph contains 259988 nodes and 833051 edges, compared to 
256137 nodes and 823496 edges before. Therefore, it seems to not make a huge
difference, but it does make a difference.

Before:

| graph             | nodes, edges | 
| ------------------|--------------| 
| Hyperlink graph   | 256137, 823496|
| Hyperlink community |  879, 6001 |
| Total graph |  507173, 1571871 |
| Total community |629, 4728 | 

New import mechanism:

| graph             | nodes, edges | 
| ------------------|--------------| 
| Hyperlink graph   | 259988, 833051|
| Hyperlink community |  729, 5376 |
| Total graph | 521935, 1584431 |
| Total community |513, 4715 | 

In the community graphs, the difference is way more significant. 
We do have to take into account that the community clustering results are 
random, but running it multiple times gives similar results (i.e. 676 nodes in 
hyperlink community, 488 in total community). It seems that while the amount of nodes and edges has increased,
the amount of communities decreases in both cases.

Speaking of which, I should probably try to get these as consistent as possible. 
Will try converting the graphs to undirected graphs and store them in separate files,
so these will be the same every time. 
-> Results still differ each time, but loading in the file is 30 times faster, so
will use the pickled files anyway. 

#### Tracking graph
Created a new graph that links on only tracking code, not on the hyperlinks.
Contains 310736 nodes and 751380 edges. That's correct, because
there should be less nodes than in the total graph (since we only add the domains
we've visited and the tracking code sources as nodes, while before we also included
the hyperlinks we found, but did not visit).
Interestingly, there are more nodes than in the hyperlinking graph, so apparently 
the average site links to more cookie and script sources than actual external domains.

The community graph contains 4060 nodes and 5724 edges. That's a lot more nodes
than the other community graphs. This kinda makes sense, because there are lots
of nodes like the following example:
```text
  node [
    id 3325
    label 3325
      scripts "piwik.rz.uni-frankfurt.de/piwik/piwik.js"
      domains "goethe-university-frankfurt.de"
    domaincount 1
    scriptcount 1
  ]
```
When a site uses a script from a third party domain, we flag it as tracking.
In this case, however, both domains are obviously owned by the same party.
Lots of smaller nodes will simply be websites that use their own scripts, but
have them stored under another domain.

The article Martin told me about:
https://www.nature.com/articles/srep04238?utm_content=buffere8bc7&utm_medium=social&utm_source=twitter.com&utm_campaign=buffer

Apparently gephi has an implementation of Louvain (or another algorithm by 
blondel et al?), but it finds 297 communities rather than 700 for the hyperlinking.
Might want to change the scale/resolution setting of the python louvain 
implementation. (note that this is on the directed graph)

Stats according to gephi for hyperlink graph:

|Metric|Value|
|------|-----|
| avg degree |  3.204  |
| avg weighted degree |  32.054  |


NOTE: should determine top 50 or so tracking code, and have a manual look at them.
Should also blacklist empty strings from all sources so we don't have accidental
connections by programming errors.

another NOTE: we still have cookies like
```text
"bcp.crwdcntrl.net/5/c=8943/rand=378563874/pv=y/adv=%23OpR%2370996%23Seattle%20Times%20%3A%20seattletimes%20%3A%20Tags%20%3A%20Sports%2C%20Other%20Sports/int=%23OpR%2370997%23Seattle%20Times%20%3A%20seattletimes%20%3A%20Total%20Site%20Traffic/int=%23OpR%2370998%23Seattle%20Times%20%3A%20seattletimes%20%3A%20Site%20Section%20%3A%20sports/int=%23OpR%2370999%23Seattle%20Times%20%3A%20seattletimes%20%3A%20Site%20Section%20%3A%20sports%20%3A%20sports-on-tv-radio-/rt=ifr"
"bcp.crwdcntrl.net/5/ct=y/c=8943/rand=381336433/pv=y/adv=%23OpR%2370996%23Seattle%20Times%20%3A%20seattletimes%20%3A%20Tags%20%3A%20Local%20News%2C%20Traffic%20Lab%2C%20Bertha/int=%23OpR%2370997%23Seattle%20Times%20%3A%20seattletimes%20%3A%20Total%20Site%20Traffic/int=%23OpR%2370998%23Seattle%20Times%20%3A%20seattletimes%20%3A%20Site%20Section%20%3A%20seattle-news/int=%23OpR%2370999%23Seattle%20Times%20%3A%20seattletimes%20%3A%20Site%20Section%20%3A%20seattle-news%20%3A%20transportation/rt=ifr"
```
These may affect the clustering results somehow (because each of them will be
regarded as a separate piece of tracking code, while it is likely the same).

### 14-05-2017
[Article](https://www.nature.com/articles/srep04238?utm_content=buffere8bc7&utm_medium=social&utm_source=twitter.com&utm_campaign=buffer
) suggests that, to determine key players in the network, degree centrality
and betweenness centrality are good metrics. 

"Degree centrality measures the number of direct contacts sur-
rounding an actor.
Because high scores on degree centrality as
associated with better access to resources, these actors are associated
with influential and powerful positions within social networks. Since
they are important for the flow of information and resources
throughout the network, these actors are called hubs. Hubs have
major influence on overall network structure, networks that gravitate
around a few hubs, for instance, are defined as ‘scale-free’ (centra-
lized) networks. In social network terms these networks are charac-
terized by a power-law degree distribution, which means that a small
percentage of actors have a large number of links."

"Betweenness-centrality incorpo-
rates the indirect contacts that surround an actor and is calculated by
the number of times that an actor serves as a bridge (shortest paths)
between other pairs of actors. Therefore betweenness centrality
represents the ability of some actors to control the flow of connec-
tivity (information, resources etc.) within the network. Because
these actors often bridge the ‘structural holes’ between disconnected
(sub)groups, these actors are called ‘brokers’. Burt explained the
importance of brokers for an increase of social capital within entre-
preneurial networks. Entrepreneurs on either side of the brokerage
position rely on the broker for indirect access to resources and
information beyond their reach. There is empirical evidence that
brokers play important roles in connecting criminal networks con-
necting separate criminal collectives within illegal markets. By
attacking these brokers, important non-redundant opportunities to
expand an illegal business might decrease. This is especially relevant
for decentralized networks, such as terrorist networks."

Furthermore, they look at amount of nodes and edges, avg degree, degree distribution,
avg shortest path, diameter and largest component.

From the degree distribution, we can derive whether the network is scale-free, etc.
(i.e. gives insight in the topology).

"Secrecy is strongly associated with the metric
of ‘network density’. Density (or the
equivalent ‘brightness’) is calculated by dividing the number of direct
connections by the maximum possible connections within the
observed network."

There are many metrics I cannot compute (connectivity, avg. shortest path, 
diameter) because the graph is disconnected. I might be able to find the biggest
component and then compute these statistics on this component, but I'm not sure
how long that would take to compute. However, that only works on the undirected
graphs.

#### Graph metrics
Will only compute avg shortest path, diameter, betweenness for the community graphs,
because the other graphs are way too big. If I really need to know, should look
at some way of parallelizing it.

Undirectional hyperlink graph:
```text
Nodes: 259988
Edges: 792038

Calculating degree distribution.
Top 10 domains by degree:
[('blogspot.com', 0.020693342359425663), ('pinterest.com', 0.027762926607868853), ('wordpress.com', 0.03002457815198452), ('linkedin.com', 0.037444179901302756), ('instagram.com', 0.05356421667237208), ('youtube.com', 0.06300315015750788), ('google.com', 0.06762261189982575), ('wikipedia.org', 0.08963525099331889), ('facebook.com', 0.12943724109282387), ('twitter.com', 0.13038344224903553)]
Average degree:
2.3435330266136364e-05
Calculating density.
2.3435330266136367e-05
Calculating largest connected component
Stats for largest component:

Nodes: 259871
Edges: 791968

Calculating degree distribution.
Top 10 domains by degree:
[('blogspot.com', 0.020702659021818604), ('pinterest.com', 0.027775426174625778), ('wordpress.com', 0.030038095971062457), ('linkedin.com', 0.0374610382114134), ('instagram.com', 0.05358833262785239), ('youtube.com', 0.06303151575787895), ('google.com', 0.06765305729787971), ('wikipedia.org', 0.08967560703428638), ('facebook.com', 0.12949551698926387), ('twitter.com', 0.13044214414899757)]
Average degree:
2.3454364253833797e-05
Calculating density.
2.3454364253833797e-05
```
Undirectional tracking graph:
```text

```
Undirectional total graph:
```text

```

Hyperlink community graph:
```text
Nodes: 699
Edges: 5383

Calculating degree distribution.
Top 10 domains by degree:
[(3, 0.19484240687679083), (24, 0.20630372492836677), (8, 0.2292263610315186), (2, 0.25787965616045844), (33, 0.27650429799426934), (20, 0.2951289398280802), (17, 0.40544412607449853), (4, 0.4699140401146132), (1, 0.5300859598853868), (6, 0.8008595988538681)]
Average degree:
0.022065906677980415
Calculating betweenness distribution
Top 10 domains by betweenness:
[(24, 0.007033025206521069), (71, 0.007065203936177349), (8, 0.009884905305683577), (2, 0.015651787521105916), (20, 0.0256046038377358), (33, 0.035611384341702156), (17, 0.08128398573692697), (4, 0.09425135448972422), (1, 0.1835531497089418), (6, 0.46375948805020123)]
Average betweenness:
0.0013624757898937606
Calculating density.
0.022065906677980415
Calculating largest connected component
Stats for largest component:

Nodes: 650
Edges: 5334

Calculating degree distribution.
Top 10 domains by degree:
[(3, 0.2095531587057011), (24, 0.2218798151001541), (8, 0.2465331278890601), (2, 0.27734976887519264), (33, 0.29738058551617874), (20, 0.3174114021571649), (17, 0.43605546995377503), (4, 0.5053929121725732), (1, 0.5701078582434514), (6, 0.8613251155624038)]
Average degree:
0.025288609695389357
Calculating betweenness distribution
Top 10 domains by betweenness:
[(24, 0.008135994980700934), (71, 0.008173220210993877), (8, 0.011435127500634629), (2, 0.018106413807907593), (20, 0.02962010261437704), (33, 0.04119621866153091), (17, 0.09403152705237257), (4, 0.10903253216576729), (1, 0.21233927945247777), (6, 0.5364895981789438)]
Average betweenness:
0.001694966468977767
Calculating density.
0.025288609695389357
Calculating average shortest path length.
2.098338271897594
Calculating diameter.
3
```

Tracking community graph:
```text
Nodes: 4056
Edges: 5636

Calculating degree distribution.
Top 10 domains by degree:
[(1, 0.015536374845869297), (8, 0.01627620221948212), (11, 0.017016029593094943), (17, 0.020715166461159062), (6, 0.021454993834771886), (28, 0.029839704069050555), (13, 0.03945745992601726), (5, 0.041183723797780514), (20, 0.04315659679408138), (4, 0.05745992601726264)]
Average degree:
0.0006853496182909062
Calculating betweenness distribution
Top 10 domains by betweenness:
[(1, 0.0002302959720903995), (11, 0.00029686513409355565), (8, 0.0003297695265231083), (17, 0.0004579937149315223), (6, 0.0006129023878982009), (28, 0.0011170469700890048), (13, 0.0022854094449634194), (5, 0.0024257939138496065), (20, 0.003305159955606601), (4, 0.0048753568150473724)]
Average betweenness:
4.045685548003144e-06
Calculating density.
0.0006853496182909063
Calculating largest connected component
Stats for largest component:

Nodes: 438
Edges: 2018

Calculating degree distribution.
Top 10 domains by degree:
[(1, 0.14416475972540047), (8, 0.15102974828375287), (11, 0.15789473684210525), (17, 0.19221967963386727), (6, 0.19908466819221968), (28, 0.2768878718535469), (13, 0.36613272311212813), (5, 0.38215102974828374), (20, 0.40045766590389015), (4, 0.5331807780320366)]
Average degree:
0.021086068357313775
Calculating betweenness distribution
Top 10 domains by betweenness:
[(1, 0.01986977818064638), (11, 0.025613319722723394), (8, 0.02845228808508592), (17, 0.03951538292752846), (6, 0.05288079675638158), (28, 0.09637804478976787), (13, 0.19718355606129298), (5, 0.20929583154512785), (20, 0.2851669292056888), (4, 0.42064243498131154)]
Average betweenness:
0.0032323816792912577
Calculating density.
0.021086068357313772
Calculating average shortest path length.
2.4093184121709874
Calculating diameter.
3
```

Total community graph:
```text
Nodes: 491
Edges: 4582

Calculating degree distribution.
Top 10 domains by degree:
[(9, 0.27346938775510204), (28, 0.28163265306122454), (18, 0.2938775510204082), (12, 0.3020408163265306), (5, 0.31836734693877555), (1, 0.33877551020408164), (10, 0.37142857142857144), (8, 0.45306122448979597), (2, 0.5795918367346939), (3, 0.6142857142857143)]
Average degree:
0.03808969616359783
Calculating betweenness distribution
Top 10 domains by betweenness:
[(19, 0.014381849162631147), (5, 0.019085434105272477), (18, 0.02050989203234545), (28, 0.020724196251257265), (1, 0.02228696768823762), (12, 0.0246631838460371), (10, 0.05725473022749226), (8, 0.08062880981103712), (2, 0.18677514952504945), (3, 0.1909324044028501)]
Average betweenness:
0.0014154195407999643
Calculating density.
0.03808969616359782
Calculating largest connected component
Stats for largest component:

Nodes: 393
Edges: 4484

Calculating degree distribution.
Top 10 domains by degree:
[(9, 0.34183673469387754), (28, 0.35204081632653056), (18, 0.36734693877551017), (12, 0.37755102040816324), (5, 0.39795918367346933), (1, 0.423469387755102), (10, 0.46428571428571425), (8, 0.5663265306122448), (2, 0.7244897959183673), (3, 0.7678571428571428)]
Average degree:
0.058212598016305746
Calculating betweenness distribution
Top 10 domains by betweenness:
[(19, 0.022483133761274397), (5, 0.029836244493216885), (18, 0.03206309847767559), (28, 0.03239812009867264), (1, 0.03484119948704666), (12, 0.038555936383350836), (10, 0.08950627583517812), (8, 0.1260469565140574), (2, 0.2919854479467685), (3, 0.2984844813075246)]
Average betweenness:
0.0027644977672449662
Calculating density.
0.05821259801630576
Calculating average shortest path length.
2.0809186269927817
Calculating diameter.
3
```

## Week 7
### 15-05-2017
Top 50 script sources:
```text
log.pinterest.com: 891
google.com/uds/api/search/1.0/584853a42cc2f90f5533642697d97114/default+en.I.js: 894
connect.facebook.net/en_US/all.js: 900
w.sharethis.com/button/p.js: 908
secure.quantserve.com/quant.js: 931
s.ytimg.com/yts/jsbin/www-widgetapi-vflP_UL_8/www-widgetapi.js: 943
platform.twitter.com/js/tweet.d3d43222534f3578c861bb67baf17e3c.js: 1003
analytics.twitter.com/i/adsct: 1025
stats.g.doubleclick.net/dc.js: 1046
apis.google.com/_/scs/apps-static/_/js/k=oz.gapi.nl.43JAI8YPjas.O/m=auth/exm=plusone/rt=j/sv=1/d=1/ed=1/am=AQ/rs=AGLTcCOl4ILqyPOrt75ObgDfKa3vVKWH-w/cb=gapi.loaded_1: 1054
pagead2.googlesyndication.com/pagead/show_ads.js: 1069
ib.adnxs.com/jpt: 1075
youtube.com/iframe_api: 1118
s1.wp.com/wp-content/mu-plugins/gravatar-hovercards/wpgroho.js: 1277
apis.google.com/js/platform.js: 1279
google-analytics.com/plugins/ua/ec.js: 1303
s2.wp.com/_static: 1305
s1.wp.com/_static: 1327
s.ytimg.com/yts/jsbin/www-widgetapi-vflktVMi7/www-widgetapi.js: 1373
r-login.wordpress.com/remote-login.php: 1430
s1.wp.com/wp-includes/js/wp-emoji-release.min.js: 1447
maps.googleapis.com/maps/api/js: 1453
stats.wp.com/e-201718.js: 1483
google.com/jsapi: 1490
script.hotjar.com/modules-bcb6f6382be530183b94c4d38f350a82.js: 1565
google.com/recaptcha/api.js: 1742
aax.amazon-adsystem.com/e/dtb/bid: 1775
gstatic.com/recaptcha/api2/r20170503135251/recaptcha__en.js: 1786
s.gravatar.com/js/gprofiles.js: 1805
apis.google.com/_/scs/apps-static/_/js/k=oz.gapi.nl.43JAI8YPjas.O/m=plusone/rt=j/sv=1/d=1/ed=1/am=AQ/rs=AGLTcCOl4ILqyPOrt75ObgDfKa3vVKWH-w/cb=gapi.loaded_0: 1815
js-agent.newrelic.com/nr-1026.min.js: 1820
edge.quantserve.com/quant.js: 1995
sb.scorecardresearch.com/beacon.js: 2209
stats.wp.com/e-201719.js: 2385
ssl.google-analytics.com/ga.js: 2579
googletagmanager.com/gtm.js: 2652
apis.google.com/js/plusone.js: 2746
google-analytics.com/plugins/ua/linkid.js: 2961
b.scorecardresearch.com/beacon.js: 3093
platform.twitter.com/js/timeline.f5dd213113d43f976c8a616c7319825a.js: 3143
s0.wp.com/wp-content/js/devicepx-jetpack.js: 3762
platform.twitter.com/js/button.90facfc7dd48c9c8c4f1fc94e137b515.js: 4231
connect.facebook.net/en_US/fbevents.js: 4864
pagead2.googlesyndication.com/pagead/osd.js: 4945
securepubads.g.doubleclick.net/gampad/ads: 5414
googletagservices.com/tag/js/gpt.js: 5688
securepubads.g.doubleclick.net/gpt/pubads_impl_116.js: 6486
platform.twitter.com/widgets.js: 7080
google-analytics.com/ga.js: 8098
google-analytics.com/analytics.js: 14117
```
Interestingly, jQuery is not even in the top 50.
How do I determine what should be classified as tracking and what shouldn't?
The twitter widget is just a retweet button etc. It might be tracking, but it might
not be.

How do we treat captcha? The newer version is tracking the users behaviour to determine
whether it's a bot, so it is definitely tracking code. However, are parties like
Google interesting for this research? I think I'll just end up grouping websites
that use facebook buttons, google captchas etc., which I assume isn't really
the point here.

Top 50 cookies:
```text
match.adsrvr.org/track/cmf/generic: 586
pixel.mathtag.com/sync/js: 596
s.amazon-adsystem.com/iu3: 607
s.amazon-adsystem.com/x/da2e6c890e6e3636: 625
apis.google.com/js/api.js: 626
cm.g.doubleclick.net/pixel: 643
sync.teads.tv/iframe/redirect: 656
ap.lijit.com/rtb/bid: 669
sync.teads.tv/iframe: 674
jadserve.postrelease.com/t: 686
presentation-ams1.turn.com/server/ads.js: 759
sync.mathtag.com/sync/img: 760
secure.adnxs.com/bounce: 765
ml314.com/tag.aspx: 779
ml314.com/utsync.ashx: 782
as.casalemedia.com/cygnus: 793
apex.go.sonobi.com/trinity.js: 859
odb.outbrain.com/utils/get: 864
track.adform.net/serving/cookie/match: 914
ad.atdmt.com/i/t.js: 923
usync.nexage.com/mapuser: 940
static.addtoany.com/menu/page.js: 943
geo-um.btrll.com/v1/map_pixel/partner/1895.png: 944
ajax.cloudflare.com/cdn-cgi/nexp/dok3v=85b614c0f6/cloudflare.min.js: 968
image2.pubmatic.com/AdServer/Pug: 987
sync.adaptv.advertising.com/sync: 987
public-api.wordpress.com/wp-admin/rest-proxy: 1014
image6.pubmatic.com/AdServer/PugMaster: 1022
ads.pubmatic.com/AdServer/js/showad.js: 1032
log.pinterest.com: 1054
ib.adnxs.com/getuid: 1102
fastlane.rubiconproject.com/a/api/fastlane.json: 1190
analytics.twitter.com/i/adsct: 1253
apis.google.com/js/platform.js: 1291
m.adnxs.com/seg: 1309
m.adnxs.com/mapuid: 1310
bat.bing.com/bat.js: 1319
c.bing.com/c.gif: 1327
ib.adnxs.com/async_usersync: 1328
googleads.g.doubleclick.net/pagead/drt/si: 1348
ib.adnxs.com/jpt: 1439
us-u.openx.net/w/1.0/pd: 1482
dpm.demdex.net/id: 1501
ib.adnxs.com/bounce: 1512
linkedin.com/countserv/count/share: 1801
l.sharethis.com/pview: 2195
apis.google.com/js/plusone.js: 3942
googleads.g.doubleclick.net/pagead/ads: 4407
securepubads.g.doubleclick.net/gampad/ads: 5059
m.addthis.com/live/red_lojson/300lo.json: 5130
```

Networkx contains a function for PageRank, but there are many parameters to be set.
Not sure how fast this would be to compute on the normal graphs, and also not sure
how useful it would be to calculate this for the community graphs. [API docs](https://networkx.github.io/documentation/networkx-1.10/reference/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html)

Have added average clustering coefficient to the default graph metrics.
Now also compute modularity in louvain.py.

### 16-05-2017
Had a meeting with Hosein to discuss the results. These metrics are probably fine, I will 
mostly focus on doing some manual analysis. For now, will reconstruct the graphs (directed 
instead of multigraphs), and calculate some of the chosen metrics. For the big graphs, this
will take some time (took about an hour for tracking graph).

### 17-05-2017
Tried k-clique clustering with k of 5, but is not done after an hour. Will try once
more with 1000 to see if it is any quicker, otherwise i'll just look into the louvain 
parameters.

1000 is done really quickly, but doesn't return anything.
Same story for 10000, 500 and 100. 10 Takes significantly longer, has not yet
returned any results but is still running.
Turns out you have to find the cliques first before you can run k-clique clustering.
Did that, doesn't actually matter for the results. Will now keep running 10 for a while to see if
anything pops up.
Printing the cliques does show many different, small cliques (size 2-15 or so).
Ran 10 for at least half an hour, still no results.

Having a look at a newly clustered Louvain community graph, websites don't necessarily
seem relevantly clustered anymore (in hyperlink graph). This may be because of the change
from multidigraph to digraph, but will have to have a look.

With resolution 0.5, seems a bit better. Websites seem to be mostly clustered on location,
but there is one huge cluster that definitely contains mostly porn sites.

Resolution 5 is definitely better. Before, surfsara.nl was either in a cluster with russian
websites or in one with world of tanks and other game websites. It is now in a cluster with
```text
      domains "surfsara.nl"
      domains "surf.nl"
      domains "surfnet.nl"
      domains "surfmarket.nl"
      domains "surfspot.nl"
```
Total nodes has increased to 12000 from 700, which seems more realistic.
However, modularity has decreased to 0.64 from 0.69.
Setting it to 50 then changes it to 0.658 and 9200 nodes. However, in Gephi this results
to only 1 'outstanding' node in the visualisation, which has 70000 domains. This doesn't seem
realistic. I suppose that a resolution of 1 or 5 is still better.
However, the surfsara remains an issue.
If i choose 5, surfsara seems to always end up correctly, and the modularity is 0.662.
That is a decrease, but not too much. However, visualising the graph in gephi does again
result in only one bigger node with 60000 domains, the rest is just 'noise' in the background.

### 18-05-2017
Removed website with domain "" from the database. Will now remove all edges to it as well,
to see if this affects the results. It's currently clustered with the russian websites,
so maybe this affects the surfsara issue as well.

This has actually solved the problem! The clusters look better now with a resolution of 1, 
the russian sites are no longer clustered with surfsara and some english websites. Surfsara 
is in its own cluster, and the russian sites seem fine too.

Have tried setting an edge weight limit of 5 to see what happens. Modularity has
significantly decreased: 0.5537174051124681
Only has 391 nodes.

Doesn't seem to significantly improve the cluster size. There are 2 nodes 30K+ and 4 nodes 20K+.
In comparison, the old graph had one 40K+, one 35K , one 20K and one 15K. 
It might decrease cluster size a little more if I further decrease the maximum weight, but
for lower than 5, I might as well use an unweighted graph, which doesn't seem realistic
for this purpose. After all, if sites link to eachother more often, they are definitely
more likely to belong to a community together.
Furthermore, surfsara is then in a seemingly random cluster again.

Interestingly, I have found the following cluster:
```text
    id 385
    label 385
    domaincount 6
      domains "dgbes.com"
      domains "seoshop.nl"
      domains "opendtect.org"
      domains "lightspeedhq.com"
      domains "lightspeedhq.nl"
      domains "spaansesloffen.nl"
```
dgbes.com and opendtect are both linked, and obviously so are the lightspeed websites.
Seoshop is just a redirect to lightspeed.
The question is then, how are they linked to spaansesloffen? Why are these three separate
groups of websites in the same cluster?

The URL that has been crawled is http://www.seoshop.nl/webwinkel-van-het-jaar-2014/.
It contains 66 hyperlinks, roughly 50 of them are lightspeedhq.nl (not actually external,
but I was already aware of this issue), and one links to lightspeedhq.com. 
Spaansesloffen.nl is indeed in there. The post is
actually about spaansesloffen.nl winning the title "webwinkel van het jaar 2014". There is
only one link to it. All other links are only to facebook, instagram, pinterest etc.

How is that connected to the opendtect and dgbes? dgbes.com links to both lightspeedhq.com
and opendtect.org. Contains no other links. All links on opendtect.org refer back to
dgbes.com. Mystery solved!

Created small script to extract a subgraph file from the original graph using a specified
community. I can then calculate metrics for these, when needed.

Judging by eye, it seems the first (biggest) community of the hyperlink community graph
is mainly linked because of wikipedia. It is a weakly connected graph:
If all edges were undirected, it would be a connected graph.

### 19-05-2017
http://www.ams.org/notices/200909/rtx090901082p.pdf paper about networks and communities

### 20-05-2017
Calculated both connectivity (networkx function) and the ratio of strongly connected component
size to total sub-graph size. Strongly connected ratio and density are almost exactly
the same, even their distributions.

16 of the sub-graphs are strongly connected, but those are likely the ones with only 2 
nodes. Have decided to use density instead.

### 21-05-2017
Will manually inspect some of the clusters and save the images, not necessarily using them
in the thesis.

## Week 8
### 22-05-2017
should redo tracking community metrics, the subgraphs only took the domains into account
and skipped the scripts and cookies.

While density and strongly connected followed almost the same distribution in the 
hyperlink communities, they are more different for the total communities.

The average connectivity of a graph G is the average of local node connectivity over all pairs of nodes of G.
http://www.sciencedirect.com/science/article/pii/S0012365X01001807 paper about avg connectivity
For every two nodes in G, how many nodes have to be removed to no longer have a path
between them

From the devot.ee cluster, the website skillshare.com has been removed. Cannot find it 
after running Louvain on the silo it is in (silo is huge, many communities). ->
manually checking the database, it uses some common google scripts or cookies, so its probably
in one of the very large clusters.

szekesvehervar is now own cluster, could not be found using louvain (will need to 
actually run louvain recursively, then try searching it in the file).

Some weird stuff:
theluxurynetwork.co.uk was found louvain, but total silo includes two domains. However,
these two do not share any cookie or scripts with the luxurynetwork cluster, its just that
both of the clusters have an outbound link to the same domain (cross.com, which does not 
have any outbound links). The community silo includes two new domains, which were in a 
completely different silo using the hyperlinks. However, they do not share any cookies or
scripts. Might be randomisation, will have to confirm by re-running total clustering.

### 28-05-2017
Highest degree in tracking graph is 14117. As each script and cookie node creates a fully connected
subgraph in the induced graph, this node alone would create 99 million new edges, because 
fully connected edges is (N(N-1))/2. Thats obviously way too many, and not feasible to produce.
The graph file will get REALLY big, and it will take really long to compute.
Therefore, taking 99.9 percentile of degree, which is 406.08.

The graph is 680 MB, making it too big to visualise. Might not be too big for metrics though.

Recalculated hyperlink community metrics on induced graph:
```
Average density: 0.5875779056725601
Average size: 7.976618705035971
Average degree: 2.3483493926825347
Average connectivity: 1.3780283742443307
```

Total communities:
```
Average density: 0.4246093471009255
Average size: 5.980392156862745
Average degree: 1.6133260783206695
Average connectivity: 0.814547685409819
```

tracking communities:
```
Average density: 0.08307182310450581
Average size: 1.0817762678961418
Average degree: 0.27493160517260684
Average connectivity: 0.177953845305611
```

Will now look into all the hierarchy levels of the clustering process, to see
if i can find some of the subreddits.

Finds 13302 communities with modularity of 0.635. 99.6% has between 20 and 100 domains.

# Graph metrics
## Normal graphs
TODO: add more metrics from giant component (on undirected graphs)
### Hyperlink
Nodes: 259988
Edges: 833051
Symmetric edges: 82026

Top 10 domains by degree:
[('blogspot.com', 0.022185724670848925), ('pinterest.com', 0.03032843949889802), ('wordpress.com', 0.033493982391427264), ('linkedin.com', 0.037459565285956606), ('instagram.com', 0.05358344840318938), ('youtube.com', 0.0653494213172197), ('google.com', 0.07051121786858573), ('wikipedia.org', 0.09346621177212706), ('twitter.com', 0.13039882763368937), ('facebook.com', 0.13122963840499716)]
Average degree: 2.4648849314723746e-05
Density: 1.2324424657361873e-05

### Tracking
Nodes: 310736
Edges: 696204
SYmmetric edges: 2

Top 10 sources by degree:
[('apis.google.com/js/plusone.js', 0.01478430173620609), ('connect.facebook.net/en_US/fbevents.js', 0.0156532093262748), ('pagead2.googlesyndication.com/pagead/osd.js', 0.01591388160329541), ('m.addthis.com/live/red_lojson/300lo.json', 0.01650924421130545), ('googletagservices.com/tag/js/gpt.js', 0.018304986564114115), ('securepubads.g.doubleclick.net/gampad/ads', 0.02054161906447616), ('securepubads.g.doubleclick.net/gpt/pubads_impl_116.js', 0.020873091219206077), ('platform.twitter.com/widgets.js', 0.022784687917357233), ('google-analytics.com/ga.js', 0.026060791349542214), ('google-analytics.com/analytics.js', 0.04543099425555538)]
Average degree: 1.4420647653175036e-05
Density: 7.210323826587519e-06
### Total
Nodes: 512935
Edges: 1528256
Symmetric edges: 82106

* Cannot calculate degree distribution for this graph, because python runs out of memory.
I can try it on the cluster later. *

Density: 5.8086109350331005e-06
## Community graphs
TODO: calculate relevant statistics (i.e. not pagerank)
### Hyperlink
Modularity: 0.6971080861741044
Nodes: 671
### Tracking
Modularity: 0.6163
Nodes: 4169
### Total
Modularity: 0.63836
Nodes: 453

## Research limitations
Ideally, we would like to use the URLs breadth-first per subreddit.
This is difficult now, because we work with one big output list of URLs that we try to index.
This is the most efficient approach, but it loses information about which URL is from where.
Therefore, it might be that when we have 10000 of 40000 seed URLs in commoncrawl, a subreddit might
be excluded completely, or another is over-represented. 

Furthermore, because we use common crawl and not every URL is present, this means we lose many 
seed URLs. Ideally, one would have a recursive crawler that picks up the URLs as it goes, because
it has to process them anyway. However, the engineering of such a programme will be too complex
for the scope of this project. -> have actually done this because of the amount of work required for 
Common Crawl vs. the simplicity it gains us. Does no longer seem worth, and the recursive crawler is
basic enough (i.e. runs on only one node) to be constructed in the limited timespan.

Reddit poster karma instead of post upvotes.

LOOK AT ALL DEGREES INSTEAD OF ISOLATED!

Induced graph max degree issue.

Although unlikely because of the results with the total graph compared to the hyperlink graph,
it may be that using the induced graph for the community detection would result in more
 interesting communities.
However, i think i can conclude that hyperlink works best to get the communities, and that
a separate approach should be taken to then analyse the tracking code in these communities.
## Crawler limitations
Could have probably used more than one node, dividing the administrative work among threads.
If we use one core less per node, that should be fine for the link processing etc.

A better lookup system can be used for the unique URLs, for example b+ trees with hashes of the URLs.

Copying the files is probably blocking the execution of the rest of the code. Would be nicer to do 
this in a separate thread/process.

Just for neatness, could/should make all parameters command line args (execution time, input file etc.).

To determine third-party cookies, I look at the domain of the URL and the domain
of the cookies. However, we might be redirected. For example, any link on bit.ly
will always be third-party, because the bit.ly actually referred us to some
other website. Therefore, it would be better to extract the url from the page
after it is loaded, and use its domain. However, I don't think the domain package
works on the worker process, so that would require a fairly complex adaptation of
the code.

## Data processing
Using the multiprocess import solution as I do, it is theoretically possible that some data
is not imported because of simultaneous acces. One process can try to store its data,
see that the domain is already in the database, and request the current db object.
While this process updates the old object locally before writing back to the database,
the database object may be overwritten by another process at the same time. If then 
the first process overwrites the object in the database (which it does), the data
that was stored intermediately is lost.

A solution for this could be that the child process returns the parsed object to the parent,
which then writes all data to the database. Because it is only one process, this ensures
that the data remains correct at all times. However, this would also form a bottleneck,
because all object modifications will have to be done by the parent as well, instead
of potentially 15 in parallel. That might not be too bad though.

Have changed it so that the master thread is indeed the only one doing the database 
updates. When run on the cluster, this took too long, have never looked what the error
might be. The local version did not have this feature, and worked fine, so I'll
just use that data. Ideally, I should fix this to see if it makes a difference though.