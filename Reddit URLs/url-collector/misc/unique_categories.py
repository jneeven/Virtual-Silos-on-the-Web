"""
This script is used to match subreddits from the 20 SFW categories as listed on
redditlist.com against eachother, leaving only those subreddits that are specific
to a category (i.e. they appear at most in one of the categories).
"""
categories = [
    'Art',
    'Culture',
    'Discussion',
    'Gaming',
    'Humor',
    'Info',
    'Lifestyle',
    'Location',
    'Meta',
    'Movies',
    'Music',
    'News And Politics',
    'Pictures',
    'Q And A',
    'Read And Write',
    'Science',
    'SFW Porn',
    'Sports',
    'Technology',
    'TV'
]


# Loop over all subreddits in a category to see if the one we are looking for is present.
# If it is, return False (not unique)
def check_category(subreddit, category):
    for other_subreddit in subreddits[category]:
        if other_subreddit == subreddit:
            return False
    return True


if __name__ == "__main__":
    subreddits = {}

    # Generate list of subreddits per category
    for category in categories:
        file = open('categories/'+category.lower() + '.txt', 'r')
        subreddits_list = []
        for line in file:
            sr = line.split(' ')[0].strip('\n').lower()
            if not sr in subreddits_list:
                subreddits_list.append(sr)

        subreddits[category.lower()] = subreddits_list

    # Find unique subreddits per category by comparing them all with each other
    uniques = {}
    for category in subreddits:
        uniques[category] = []
        for subreddit in subreddits[category]:
            unique = True
            for other_category in subreddits:
                if other_category == category:
                    continue
                if not check_category(subreddit, other_category):
                    unique = False
                    break
            if unique:
                uniques[category].append(subreddit)

    # Print unique subreddits per category
    for category in uniques:
        print("Unique subreddits for category {}:".format(category))
        print(uniques[category])

