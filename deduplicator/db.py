import psycopg2
import marshal
import logging

log = None


class Db(object):
    '''
    classdocs
    '''

    conn = None

    def __init__(self, connstr):
        '''Connects to database'''
        global log
        log = logging.getLogger('pgdocgen')
        log.setLevel(10)
        self.conn = psycopg2.connect(connstr)

    def dump_cache(self, cache):
        '''save processed data to file'''
        with open('/tmp/dedup_cache.pyc', 'wb') as fd:
            marshal.dump(cache, fd)

    def load_cache(self):
        '''load previously processed data from file'''
        with open('/tmp/dedup_cache.pyc', 'rb') as fd:
            return marshal.load(fd)

    def load_iptable(self, mindate, chunk_interval, callback):
        '''Loads new data from iptable starting from mindate
        (or all data if mindate=None) in chunks (to avoid OOM)
        calls callback for each chunk of data'''
        cur = self.conn.cursor()
        sql = '''select user_id,
                        ip_address
                from iptable
                where "date" >= %s
                and "date" < %s'''
        while True:
            if mindate:
                maxdate = mindate + chunk_interval
            log.debug('Executing SQL query (iptable)')
            log.debug('Mindate={}, Maxdate={}'
                      .format(mindate, maxdate))
            cur.execute(sql, (mindate, maxdate))
            chunk = cur.fetchall()
            log.debug('SQL Query finished')
            if len(chunk) == 0:
                # we should check if there is more data
                # outside our time interval
                log.debug('No data in interval. Seeking...')
                cur.execute('''select min("date")
                               from iptable
                               where "date" >= %s
                            ''', (maxdate,)
                            )
                # min() always returns value,
                # so no KeyError here
                mindate = cur.fetchone()[0]
                if mindate:
                    log.debug('Found data at {}'.format(mindate))
                    continue
                else:
                    break
            callback(chunk)
            mindate = maxdate
        cur.close()
        # converting to timestamp to avoid serialization error
        return (maxdate - 2*chunk_interval).timestamp()
