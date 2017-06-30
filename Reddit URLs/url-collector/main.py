"""
This file is used to crawl subreddits and gather the posted and commented URLs.
A list of Reddit account usernames and passwords should be provided, as well as some
API keys. I have used multiple credentials and switched them after a while, because
otherwise the server would just stop responding at some point.

No arguments, simply run with python main.py.
"""


import datetime
import time
import praw
import re

'''Authenticated instance of Reddit'''
# --------------------------------------------------------------------
client_ids = []
client_secrets = []
user_agents = []
usernames = []
passwords = []


'''Data retrieval functions'''
# --------------------------------------------------------------------


def get_date(submission):
    time = submission.created_utc
    return datetime.datetime.fromtimestamp(time)


# Store values as tab separated string
def output(url, score, post, date):
    # Skip references starting with hashtags, as these are not links.
    if url[0] == '#':
        return

    try:
        global url_counter
        file.write('{}\t{}\t{}\t{}\n'.format(url, score, post, date))
        url_counter += 1

        if url_counter % 100 == 0:
            print("Collected {} URLs".format(url_counter))

    except UnicodeEncodeError:
        print("Invalid characters encountered. Skipping this one.")
    except Exception as e:
        print("error:", e)


def parse_comment(comment, level=0):
    if url_counter >= url_limit or datetime.datetime.utcnow() > end_time:
        return
    body = comment.body_html
    for result in re.finditer(r'<a\s+(?:[^>]*?\s+)?href=(["\'])(.*?)\1', body):
        output(result.group(2), comment.score, int(False), get_date(comment))

    # Keep trying to load replies, our internet/the server may be down.
    while True:
        try:
            comment.replies.replace_more(limit=None)
            break
        except:
            pass

    if level <= 3:
        for reply in comment.replies:
            parse_comment(reply, level + 1)


def parse_submission(submission):
    if url_counter >= url_limit or datetime.datetime.utcnow() > end_time:
        return

    body = submission.selftext_html
    # search for URLs
    if body is not None:
        for result in re.finditer(r'<a\s+(?:[^>]*?\s+)?href=(["\'])(.*?)\1', body):
            output(result.group(2), submission.score, int(True), get_date(submission))

    # Load all top-level comments, order by descending rank
    submission.comment_sort = 'top'
    # Keep trying to load replies, our internet/the server may be down.
    while True:
        try:
            submission.comments.replace_more(limit=None)
            break
        except:
            pass

    global last_date
    last_date = get_date(submission)
    output(submission.url, submission.score, int(True), last_date)

    # Recursively parse all comments (with a maximum of 2000 top-level comments)
    comment_counter = 0
    for comment in submission.comments:
        parse_comment(comment)
        comment_counter += 1
        # Set to 2000 for subreddits, 1000 for front page top
        if comment_counter > 2000:
            break


def parse_subreddit(date):
    submissions = subreddit.submissions(end=date)
    try:
        submission = next(submissions)
        print("Connection established, collecting URLs")
    except Exception as e:
        print(e)
        print("Failed to get submissions. Trying again in a second")
        time.sleep(1)
        parse_subreddit(date)
        return

    while submission and url_counter < url_limit and datetime.datetime.utcnow() < end_time:
        parse_submission(submission)

        # Try obtaining the next post. If none exists, exit. If server overload, try again.
        try:
            submission = next(submissions)
        except StopIteration:
            break
        except:
            print("Failed to get submissions. Trying again in a second")
            time.sleep(1)
            global last_date
            parse_subreddit(time.mktime(last_date.timetuple()))
            return


def setup(out_name, reddit_idx, url_lim):
    global url_counter, reddit, file, end_time, url_limit, last_date
    file = open(out_name, 'w')

    # Switch account every time
    reddit = praw.Reddit(client_id=client_ids[reddit_idx],
                         client_secret=client_secrets[reddit_idx],
                         user_agent=user_agents[reddit_idx],
                         username=usernames[reddit_idx],
                         password=passwords[reddit_idx])

    reddit.read_only = True

    file.write("Starting time:\t{}\n".format(datetime.datetime.utcnow()))
    last_date = datetime.datetime.strptime('01-03-2017', '%d-%m-%Y')
    last_date = time.mktime(last_date.timetuple())
    end_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    url_counter = 0
    url_limit = url_lim


def parse_top():
    output_name = 'output/raw_data/' + 'top' + '.csv'
    # Set URL limit to 100000
    setup(output_name, 0, 100000)

    print("Connecting to reddit front page, getting top posts from last week")
    submissions = reddit.front.top('week')
    submission = next(submissions)
    while submission and datetime.datetime.utcnow() < end_time:
        parse_submission(submission)
        submission = next(submissions)


def parse_new():
    output_name = 'output/raw_data/' + 'new' + '.csv'

    # Set url limit to 100000
    setup(output_name, 0, 100000)

    # Reddit uses the amount of seconds after 1 january 1970.
    max_date = datetime.datetime.strptime('01-03-2017', '%d-%m-%Y')
    min_date = max_date - datetime.timedelta(weeks=1)

    max_seconds = int((max_date - datetime.datetime(1970, 1, 1)).total_seconds())
    min_seconds = int((min_date - datetime.datetime(1970, 1, 1)).total_seconds())

    print("Connecting to reddit front page, getting posts from before 1 March 2017")
    result = reddit.get('/search?sort=new&q=timestamp%3A' + str(min_seconds) +
                        '..' + str(max_seconds) + '&restrict_sr=on&syntax=cloudsearch' + '&limit=' + str(1000))

    submissions = result.children

    last_submission = None
    while datetime.datetime.utcnow() < end_time:
        for submission in submissions:
            if datetime.datetime.utcnow() < end_time:
                last_submission = submission
                parse_submission(submission)
            else:
                break

        # Get the next batch
        while True:
            try:
                url = '/search?sort=new&q=timestamp%3A' + str(min_seconds) + '..' + str(max_seconds) +\
                      '&restrict_sr=on&syntax=cloudsearch&after=' + last_submission.name + '&limit=' + str(1000)

                submissions = reddit.get(url).children
                # If we ran out of pages, create a new query with the time of the last processed post.
                if len(submissions) == 0:
                    last_seconds = int((get_date(last_submission) - datetime.datetime(1970, 1, 1)).total_seconds())
                    url = '/search?sort=new&q=timestamp%3A' + str(min_seconds) + '..' + str(last_seconds) + \
                          '&restrict_sr=on&syntax=cloudsearch&limit=' + str(1000)
                    submissions = reddit.get(url).children

                print('Parsing ', url)
                break
            except:
                print("Server not responding. Trying again in a second")
                time.sleep(1)


'''LOOP OVER SUBMISSIONS'''
# --------------------------------------------------------------------

if __name__ == '__main__':
    categories = {
        'Art': ['alternativeart', 'graphic_design'],
        'Culture': ['cyberpunk', 'opieandanthony'],
        'Discussion': ['rant', 'socialskills', 'mensrights'],
        'Gaming': ['leagueoflegends', 'casualnintendo', 'gaming'],
        'Humor': ['scenesfromahat', 'blackpeopletwitter', 'bikinibottomtwitter'],
        'Info': ['abrathatfits', 'explainlikeimfive'],
        'Lifestyle': ['fitness', 'makeupaddiction', 'relationship_advice'],
        'Location': ['losangeles', 'croatia', 'turkey'],
        'Movies': ['movies', 'netflixbestof'],
        'Music': ['music', 'kpop', 'popheads'],
        'News And Politics': ['socialism', 'hillaryclinton', 'the_donald'],
        'Pictures': ['perfectfit', 'highqualitygifs', 'abandonedporn'],
        'Q And A': ['iama', 'samplesize'],
        'Read And Write': ['writing', 'fountainpens'],
        'Science': ['science', 'space', 'chemistry'],
        'SFW Porn': ['historyporn', 'gentlemanboners', 'militaryporn'],
        'Sports': ['mma', 'eagles', 'reddevils'],
        'Technology': ['android', 'jailbreak', 'windowsphone'],
        'TV': ['strangerthings', 'community', 'rickandmorty']
    }

    url_counter, url_limit = 0, 0
    reddit, file, end_time, last_date = None, None, None, None

    # parse_top()
    parse_new()
    exit(0)

    # Parse all the subreddits in each category
    reddit_index = 0
    for i in range(0, 3):
        for category_name in categories:
            # Pick different account
            reddit_index += 1
            if reddit_index > 3:
                reddit_index = 0

            try:
                subreddit_name = categories[category_name][i]
            except IndexError:
                continue

            # Create empty output file
            filename = 'output/raw_data/' + subreddit_name + '.csv'

            # URL limit 5000
            setup(filename, reddit_index, 5000)

            subreddit = reddit.subreddit(subreddit_name)
            print("Connecting to subreddit", subreddit_name)
            parse_subreddit(last_date)

