"""
Calculate and save post and comment score distributions for each of the subreddits.
Threshold is calculated on /r/the_donald, see thesis for more information.
Post and comment thresholds for each subreddit are saved in the output folder.

No arguments, simply run with python histogram.py
"""
import matplotlib.pyplot as plt
import csv
import os
import numpy as np
from scipy import stats


def create_histogram(data, threshold, title):
    fig = plt.figure()

    left, right = np.percentile(data, [1, 95])

    n, bins, patches = plt.hist(data, bins=np.arange(left, right + 1), cumulative=False, weights=np.zeros_like(data) + 1. / len(data), facecolor='green', alpha=0.75)

    if threshold is not None:
        plt.axvline(x=threshold, color='red', linewidth=0.5)
        plt.legend(['threshold:' + str(threshold)])

    plt.xlim(left, right)
    plt.xlabel('Score')
    plt.ylabel('Relative frequency')
    plt.title(title)
    plt.grid(True)
    return fig


def multiplot(data, index, xlabel, threshold):
    threshold = np.percentile(data, threshold)
    fig = plt.subplot(120 + index)

    # If no values bigger than zero, don't plot.
    maxv = np.max(data)
    if maxv == 0:
        return

    left = 0
    right = np.log10(np.max(data))
    if right < 1:
        left = -2
    bins = np.logspace(left, right, 50)

    n, bins, patches = plt.hist(data, bins=bins, facecolor='green', log=True, alpha=0.75)
    plt.xlabel(xlabel)
    fig.set_xscale("log")
    plt.axvline(x=threshold, color='red', linewidth=0.5)
    plt.legend(['threshold:' + str(threshold)])
    if index % 2 != 0:
        plt.ylabel('Frequency')
    plt.grid(True)
    return fig


def save_comment_histogram(data, subreddit, title):
    threshold = np.percentile(data, percentile_threshold)
    comment_threshold_file.write('{}\t{}\n'.format(subreddit, threshold))
    fig = create_histogram(data, threshold, title)
    # If it does not exist, create the folder
    folder = 'output/figures/' + subreddit + '/'
    try:
        os.makedirs(folder)
    except:
        pass
    plt.savefig(folder + 'comment_distribution.pdf', bbox_inches='tight')
    plt.close(fig)


def save_post_histogram(data, subreddit, title):
    # The threshold does not apply to top, as they are sorted by score in descending order.
    if subreddit != 'top':
        threshold = np.percentile(data, percentile_threshold)
        post_threshold_file.write('{}\t{}\n'.format(subreddit, threshold))
        fig = create_histogram(data, threshold, title)
    else:
        fig = create_histogram(data, None, title)

    # If it does not exist, create the folder
    folder = 'output/figures/' + subreddit + '/'
    try:
        os.makedirs(folder)
    except:
        pass
    plt.savefig(folder + 'post_distribution.pdf', bbox_inches='tight')
    plt.close(fig)


def parse_file(filename):
    file = open('output/raw_data/' + filename, 'r', encoding="latin-1")
    reader = csv.reader(file, delimiter='\t')
    # Skip first row
    start_time = next(reader)[1]

    post_scores = []
    comment_scores = []

    print('parsing', filename)
    for row in reader:
        post = row[2]
        score = int(row[1])
        if post == '1':
            post_scores.append(score)
        else:
            comment_scores.append(score)

    return post_scores, comment_scores


def find_percentile_donald():
    post_scores, comment_scores = parse_file('the_donald.csv')
    percentile_threshold = stats.percentileofscore(post_scores, 25)
    print("Percentile of 25 upvotes for posts in the_donald:", percentile_threshold)

    post_scores, comment_scores = parse_file('android.csv')
    multiplot(post_scores, 1, 'Post score', percentile_threshold)
    multiplot(comment_scores, 2, 'Comment score', percentile_threshold)
    plt.suptitle("Post and comment score distributions of /r/science")
    plt.show()
    return percentile_threshold


if __name__ == "__main__":
    post_threshold_file = open('output/post_thresholds.csv', 'w', encoding='latin-1')
    comment_threshold_file = open('output/comment_thresholds.csv', 'w', encoding='latin-1')

    percentile_threshold = find_percentile_donald()

    for file_name in os.listdir('output/raw_data'):
        subreddit = file_name.split('.')[0]
        post_scores, comment_scores = parse_file(file_name)
        save_comment_histogram(comment_scores, subreddit, 'Comment score distribution of ' + subreddit)
        save_post_histogram(post_scores, subreddit, 'Post score distribution of ' + subreddit)

    post_threshold_file.close()
    comment_threshold_file.close()
