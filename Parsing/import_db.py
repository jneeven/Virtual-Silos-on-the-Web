"""
Import the merged data file into a locally running MongoDB, grouping the URLs by their
domains. This is a slow process; expect it to take anywhere between one and four hours.
"""

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from multiprocessing import Pool
import fileinput
import json
import time


def update_object(old, new):
    # Increase counters
    old['amtErrors'] += new['amtErrors']
    old['links'][0] += new['links'][0]
    old['links'][1] += new['links'][1]

    # Extend lists
    old['cookies'] += new['cookies']
    old['scripts'] += new['scripts']
    old['hyperlinks'] += new['hyperlinks']
    old['urls'] += new['urls']

    return old


def edit_or_insert(obj):
    domain = obj['domain']
    obj["_id"] = domain

    # Reshape the way we store the url and robots
    obj['urls'] = [{'url': obj['url'], 'robots': obj['robots']}]
    del obj['url']
    del obj['robots']

    try:
        domains.insert_one(obj)
    except DuplicateKeyError:
        old = domains.find_one({"_id": domain})
        new = update_object(old, obj)
        domains.replace_one({"_id": domain}, new, upsert=False)


def process_entry(offset, size):
    # Specify output file
    data = open('merged_output', 'rb')
    # here 'merged_output' is the path to the data file to be parsed into a mongoDB

    # Set offset from beginning
    data.seek(offset)
    text = data.read(size).decode('utf-8')
    try:
        obj = json.loads(text)
        data.close()
        return obj
    except Exception as e:
        # TODO: split data into two objects and insert both
        data.close()
        return None


def import_objects(completed):
    global last_batch
    print("Importing objects")
    counter = 0
    for task in completed:
        obj = task.get()
        if obj:
            edit_or_insert(obj)
            counter += 1
            if counter % 1000 == 0:
                print("Imported {} objects, took {} seconds.".format(counter, time.time() - last_batch))
                last_batch = time.time()
    print("processed {} objects".format(counter))


def parse_offsets():
    pool = Pool(processes=3)
    parsed = []
    prev_offset = 0
    print("Reading data")
    # Loads lines lazily so we don't have everything in memory
    for line in fileinput.input('offsets.csv'):
        # Skip the first line, because we cannot yet calculate the chunk size from it
        if fileinput.isfirstline():
            continue
        offset = int(line)
        size = offset - prev_offset
        # Somehow, the same offset rarely occurs twice in a row.
        if size != 0:
            parsed.append(pool.apply_async(process_entry, (prev_offset, size)))
            prev_offset = offset

    import_objects(parsed)


if __name__ == '__main__':
    client = MongoClient('localhost', 27017, connect=False)
    db = client['second']
    domains = db.domains

    start = time.time()
    last_batch = time.time()
    parse_offsets()
    print("All data has been imported. Took {} seconds.".format(time.time() - start))
