#!/usr/bin/env python
import threading
import requests
import time
import queue
import unittest
import logging
import sys


min_time = 100000.0
max_time = 0.000001
cnt = 0
cnt_err = 0
real_time = 0
data_lock = threading.Lock()


def check_response(r):
    return r["duplicates"] == True


def update_data(start, stop, valid):
    global min_time
    global max_time
    global cnt
    global real_time
    global data_lock
    global cnt_err
    with data_lock:
        if not valid:
            cnt_err = cnt_err + 1
        elapsed = stop - start
        real_time = real_time + elapsed
        if elapsed < min_time:
            min_time = elapsed
        if elapsed > max_time:
            max_time = elapsed
        cnt = cnt+1


def run(q):
    while True:
        try:
            address = q.get_nowait()
        except queue.Empty:
            return None
        start = time.time()
        try:
            r = requests.get(address)
            valid = check_response(r.json())
        except Exception as e:
            print('Exception: {}'.format(str(e)))
            valid = False
        update_data(start, time.time(), valid)
        q.task_done()


class LoadTest(unittest.TestCase):

    def test_highload(self):
        logging.basicConfig(stream=sys.stderr)
        log = logging.getLogger('highload')
        log.setLevel(logging.INFO)

        address = 'http://localhost:8000/1/2'
        threads = 50
        num = 10

        q = queue.Queue()
        for _ in range(threads*num):
            q.put(address)

        start = time.time()

        for _ in range(threads):
            t = threading.Thread(target=run, args=[q])
            t.daemon = True
            t.start()

        q.join()
        log.warning("Total gets: {0}".format(cnt))
        log.warning("Errors: {}".format(cnt_err))
        log.warning("Elapsed Time: {0}".format(time.time() - start))
        log.warning("Real Time: {0}".format(real_time))
        log.warning("min/avg/max get time: {0}/{1}/{2}"
                    .format(min_time,
                            real_time / cnt,
                            max_time))
        self.assertEqual(cnt_err, 0, "Errors during highload test")
