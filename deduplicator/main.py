import datetime
import threading
import logging
from time import sleep
from http.server import HTTPServer
from configparser import ConfigParser
from deduplicator.db import Db
from deduplicator.server import DupServer


# Quick and dirty globals ok for
# a test, I presume
ip_tree = {}
one_match = {}
dupes = set()
mindate = None
log = None
settings = {}


def init_logging():
    lg_format = '%(asctime)s : - %(message)s'
    logging.basicConfig(format=lg_format)
    log = logging.getLogger('duplicates')
    log.setLevel(10)
    return log


def load_config():
    '''Load settings from configfile'''
    config = ConfigParser()
    section = 'deduplicator'
    try:
        config.read('deduplicator.ini')
    except Exception as e:
        log.error('Failed to read config: ' + str(e))
        exit(1)
    for option in config.options(section):
        settings[option] = config.get(section, option)
    return settings


def build_dupes_set(chunk):
    '''Builds (or incrementally updates)
    set of tuples (user_id1, user_id2)
    where user_id1 < user_id2 and they have at least two
    common IPs from different class C networks'''
    log.debug('Build dupes called')
    cnt_records = 0
    cnt_dupes = 0
    for rec in chunk:
        cnt_records = cnt_records + 1
        # Not shure if id is integer
        # making it str to be safe
        user_id = str(rec[0])
        octets = rec[1].split('.')
        # more compact integer representation for net
        net = int(octets[0]) * 256**2 + int(octets[1]) * 256 + int(octets[2])
        host = octets[3]
        if net not in ip_tree:
            ip_tree[net] = {}
        if host not in ip_tree[net]:
            ip_tree[net][host] = set()
        if user_id not in ip_tree[net][host]:
            for other_user_id in ip_tree[net][host]:
                pair = (min(user_id, other_user_id),
                        max(user_id, other_user_id))
                if pair in dupes:
                    continue
                if pair in one_match:
                    if one_match[pair] != net:
                        dupes.add(pair)
                        del one_match[pair]
                        cnt_dupes = cnt_dupes + 1
                else:
                    one_match[pair] = net
            ip_tree[net][host].add(user_id)
    del chunk
    log.debug("Processed {} records. Found {} duplicates"
              .format(cnt_records, cnt_dupes))


def get_new_data(datasource, onetime=False):
    '''Gets new data from iptable and saves fresh cache to disk
    Unless onetime is set to True works forever.'''
    while True:
        # sleep for 1 minute to reduce
        # load on a database
        if not onetime:
            sleep(60*1)
        log.debug("Loading new data from PostgreSQL")
        global mindate
        ts = datasource.load_iptable(mindate,
                                     datetime.timedelta(hours=6),
                                     build_dupes_set)
        mindate = datetime.datetime.fromtimestamp(ts)
        # save computed structures to a file
        log.debug("Saving cache")
        datasource.dump_cache((ts, ip_tree, one_match, dupes))
        log.debug("Cache saved")
        if onetime:
            return


def are_users_duplicate(_, user1_id, user2_id):
    '''Returns true if users are duplicates
    as defined in build_dupes_set'''
    pair = (min(user1_id, user2_id),
            max(user1_id, user2_id))
    return pair in dupes


if __name__ == '__main__':
    log = init_logging()
    settings = load_config()
    datasource = Db(settings["connect_string"])
    try:
        # loading precomputed data from cache
        log.debug("Trying to load data from cache")
        (mindate, ip_tree, one_match, dupes) =\
            datasource.load_cache()
        mindate = datetime.datetime.fromtimestamp(mindate)
        log.debug("Loaded data from cache")
    except:
        mindate = datetime.datetime(year=2000, month=1, day=1)
        log.debug("Failed to load data from cache")

    # update data synchronously on start
    get_new_data(datasource, onetime=True)

    # start thread to periodically get new data
    data_thread = threading.Thread(target=get_new_data,
                                   args=[datasource])
    data_thread.daemon = True
    data_thread.start()

    print("Server is ready to accept requests.\nPress Ctrl+C to exit.")
    try:
        DupServer.is_dup = are_users_duplicate
        httpd = HTTPServer((settings['host'],
                            int(settings['port'])),
                           DupServer)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Bye!")
