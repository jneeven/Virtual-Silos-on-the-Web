"""
Filter the previously collected URLs by score, blacklist and file extension.
Final list of URLs is saved in output/filtered_urls.csv.

No arguments, simply run python filter_urls.py
"""


import csv
import os
import numpy as np
from urllib.parse import urlsplit, urlunsplit
import matplotlib.pyplot as plt

blacklist = ['youtube.com', 'youtu.be', 'reddit.com', 'instagram.com', 'imgur.com', 'streamable.com',
             'redd.it', 'twitter.com', 'facebook.com', 'reddituploads.com', 'gfycat.com', 'giphy.com',
             'staticflickr.com', 'twimg.com', 'pinimg.com', 'vimeo.com']

video_formats = ['.webm', '.mkv', '.flv', '.flv', '.vob', '.ogv', '.ogg', '.drc', '.gif', '.gifv', '.mng', '.avi', '.mov', '.qt', '.wmv', '.yuv', '.rm', '.rmvb', '.asf', '.amv', '.mp4', '.m4p', '.m4v', '.mpg', '.mp2', '.mpeg', '.mpe', '.mpv', '.mpg', '.mpeg', '.m2v', '.m4v', '.svi', '.3gp', '.3g2', '.mxf', '.roq', '.nsv', '.flv', '.f4v', '.f4p', '.f4a', '.f4b']
image_formats = ['.ani', '.bmp', '.cal', '.fax', '.gif', '.img', '.jbg', '.jpe',  '.jpeg',  '.jpg',  '.mac', '.pbm', '.pcd', '.pcx', '.pct', '.pgm', '.png', '.ppm', '.psd', '.ras', '.tga',  '.tiff',  '.wmf']
audio_formats = ['.3gp', '.aa', '.aac', '.aax', '.act', '.aiff', '.amr', '.ape', '.au', '.awb', '.dct', '.dss', '.dvf', '.flac', '.gsm', '.iklax', '.ivs', '.m4a', '.m4b', '.m4p', '.mmf', '.mp3', '.mpc', '.msv', '.ogg, ', '.oga, mogg', '.opus', '.ra, ', '.rm', '.raw', '.sln', '.tta', '.vox', '.wav', '.wma', '.wv', '.webm']
all_formats = video_formats + image_formats + audio_formats


# Create figure of top 50 linked domains
def create_overview(subreddit, domains, filtered):
    if filtered:
        # title = 'Top 50 linked websites in ' + subreddit + ' (filtered)'
        filename = 'output/figures/' + subreddit + '/top_50_links_filtered.pdf'
    else:
        # title = 'Top 50 linked websites in ' + subreddit + ' (unfiltered)'
        filename = 'output/figures/' + subreddit + '/top_50_links_unfiltered.pdf'

    fig = plt.figure()

    unique, counts = np.unique(domains, return_counts=True)

    count_array = np.array([unique, counts], dtype=np.object).T
    idx = np.argsort(count_array[:, 1])
    sorted = count_array[idx][-50:]

    h = plt.bar(np.arange(0, sorted.shape[0]), np.flipud(sorted[:, 1]))
    xticks_pos = [0.65 * patch.get_width() + patch.get_xy()[0] for patch in h]
    plt.xticks(xticks_pos, np.flipud(sorted[:, 0]), ha='right', rotation=60)
    plt.ylabel('Frequency')
    plt.yscale('log')

    # plt.title(title)
    plt.tight_layout()
    plt.show()
    # plt.savefig(filename, bbox_inches='tight')
    plt.close(fig)


# Check if the given domain is part of our blacklist, deciding if we allow it to pass
def check_blacklist(netloc):
    split = netloc.split('.')
    site = ".".join(split[-2:])
    if site not in blacklist:
        return True
    return False


def check_extension(path):
    split = path.split('.')
    if len(split) > 1:
        extension = '.' + split[-1].lower()
        if extension in all_formats:
            return False
    return True


# If not blacklisted, return url. Otherwise, return false.
def filter_url(url):
    split = urlsplit(url, allow_fragments=False)

    if split.netloc and split.netloc[0] != '/' and check_blacklist(split.netloc):
        path = '' if not split.path else split.path.split('#')[0]
        if check_extension(path):
            result = urlunsplit((split.scheme, split.netloc, path, None, None))
            return result.lower()

    return False


# Get domain of url (i.e. 'test.google.com' returns 'google.com')
def get_domain(url):
    split_url = urlsplit(url, allow_fragments=False)
    if split_url.netloc:
        split = split_url.netloc.split('.')

        if split[-1] == '':
            return False

        # .co.uk, .com.au, etc. Some strings are malformed, so we need a length check
        if len(split) >= 3 and (split[-2] == 'co' or split[-2] == 'com'):
            domain = ".".join(split[-3:])
        else:
            domain = ".".join(split[-2:])

        return domain

    # If the link is not external (i.e. '/r/testurl'), return reddit.com
    return 'reddit.com'


def parse_file(filename):
    subreddit = filename.split('.')[0]

    input_file = open('output/raw_data/' + filename, 'r', encoding="latin-1")

    reader = csv.reader(input_file, delimiter='\t')
    # Skip first row
    start_time = next(reader)[1]

    post_threshold = post_thresholds[subreddit]
    comment_threshold = comment_thresholds[subreddit]

    unfiltered_domains = []
    filtered_domains = []

    print('parsing', filename)
    for row in reader:
        post = row[2]
        score = int(row[1])
        # Pick all submissions above threshold, except for new, where we pick all those below the threshold.
        if (subreddit != 'new' and ((post == '1' and score >= post_threshold) or (post == '0' and score >= comment_threshold))) \
                or (subreddit == 'new' and ((post == '1' and score < post_threshold) or (post == '0' and score < comment_threshold))):

            # If the url is malformed, do not add it to any list.
            domain = get_domain(row[0])
            if domain:
                unfiltered_domains.append(domain)
            else:
                continue

            allowed_url = filter_url(row[0])
            if allowed_url:
                filtered_domains.append(get_domain(allowed_url))

    input_file.close()

    create_overview(subreddit, unfiltered_domains, False)
    create_overview(subreddit, filtered_domains, True)


def write_urls(url_list):
    print('Writing URLs to file')
    output_file = open('output/filtered_urls.csv', 'w', encoding='latin-1')
    for url in np.unique(url_list):
        output_file.write(url + '\n')
    output_file.close()


def parse_all():
    print("all at once:")

    output_urls = []

    unfiltered_domains = []
    filtered_domains = []

    for filename in os.listdir('output/raw_data'):
        subreddit = filename.split('.')[0]

        input_file = open('output/raw_data/' + filename, 'r', encoding="latin-1")

        reader = csv.reader(input_file, delimiter='\t')
        # Skip first row
        start_time = next(reader)[1]

        post_threshold = post_thresholds[subreddit]
        comment_threshold = comment_thresholds[subreddit]

        print('parsing', filename)
        for row in reader:
            post = row[2]
            score = int(row[1])

            # Pick all submissions above threshold, except for new, where we pick all those below the threshold.
            if (subreddit != 'new' and ((post == '1' and score >= post_threshold) or (post == '0' and score >= comment_threshold)))\
                    or (subreddit == 'new' and ((post == '1' and score < post_threshold) or (post == '0' and score < comment_threshold))):
                # If the url is malformed, do not add it to any list.
                domain = get_domain(row[0])
                if domain:
                    unfiltered_domains.append(domain)
                else:
                    continue

                allowed_url = filter_url(row[0])
                if allowed_url:
                    filtered_domains.append(get_domain(allowed_url))
                    output_urls.append(allowed_url)

        input_file.close()

    create_overview('all', unfiltered_domains, False)
    create_overview('all', filtered_domains, True)

    write_urls(output_urls)


def get_thresholds():
    post_thresh = {}
    comment_thresh = {}

    post_file = open('output/post_thresholds.csv', 'r', encoding='latin-1')
    comment_file = open('output/comment_thresholds.csv', 'r', encoding='latin-1')

    reader = csv.reader(post_file, delimiter='\t')
    for row in reader:
        post_thresh[row[0]] = float(row[1])

    post_thresh['top'] = 0.0

    reader = csv.reader(comment_file, delimiter='\t')
    for row in reader:
        comment_thresh[row[0]] = float(row[1])

    return post_thresh, comment_thresh


if __name__ == '__main__':
    post_thresholds, comment_thresholds = get_thresholds()

    parse_all()
    exit(0)

    print("Each individually:")
    for file_name in os.listdir('output/raw_data'):
        parse_file(file_name)
