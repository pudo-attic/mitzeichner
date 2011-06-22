import logging
import sys
from itertools import count
from Queue import Queue
from threading import Thread
from lxml import html
import urllib2
from core import db, Mitzeichner
from delegation import delegations

INDEX_URL = 'https://epetitionen.bundestag.de/index.php?action=petition&sa=list%s&limit=100&start=%s'
SIGN_URL = 'https://epetitionen.bundestag.de/index.php?action=petition&sa=sign&petition=%s&limit=100&start=%s'

def threaded(items, func):
    queue = Queue(maxsize=1000)
    def queue_consumer():
        while True:
            item = queue.get(True)
            try:
                func(item)
            except Exception, e:
                logging.exception(e)
            queue.task_done()

    for i in range(10):
         t = Thread(target=queue_consumer)
         t.daemon = True
         t.start()

    for item in items:
        queue.put(item, True)



def urldoc(url, *a):
    print url % a
    fh = urllib2.urlopen(url % a)
    doc = html.parse(fh)
    fh.close()
    return doc


def index(lists):
    for list_ in lists:
        last_set = set()
        for i in count():
            page = set()
            doc = urldoc(INDEX_URL, list_, i*100)
            for row in doc.findall('//tr'):
                cols = list(row.findall('.//td'))
                if len(cols) != 6:
                    continue
                id, title, creator, end_date, s_count, forum = cols
                title = title.xpath("string()").strip()
                theme = ''
                if ' - ' in title:
                    theme, title = title.split(' - ', 1)
                yield (id.text, theme, title, creator.text, end_date.text)
                page.add(id.text)
            #print page
            if last_set.intersection(page) == page:
                break
            last_set = page

def signatories(a):
    id, theme, title, creator, end_date = a
    last_set = set()
    for i in count():
        page = set()
        doc = urldoc(SIGN_URL, id, i*100)
        for row in doc.findall('//tr'):
            cols = list(row.findall('td'))
            if len(cols) != 4: 
                continue
            n, name, loc, date = map(lambda c: c.text, cols)
            persist(id, n, theme, title, creator, end_date, name, loc, date)
            page.add(n)
        if last_set.intersection(page) == page:
            break
        last_set = page
    db.session.commit()

def persist(petition_id, signer_id, theme, title, creator, end_date, name,
        location, sign_date):
    if not Mitzeichner.by_petition_signer(petition_id, signer_id):
        mitzeichner = Mitzeichner(petition_id, signer_id, theme, title, creator, end_date, name,
                location, sign_date)
        db.session.add(mitzeichner)
        delegations(mitzeichner)

if __name__ == '__main__':
    if not len(sys.argv) == 2:
        raise ValueError("Need to give a command: full, current")
    if sys.argv[1] == 'full':
        threaded(index([2, 3, 4]), signatories)
    elif sys.argv[1] == 'current':
        threaded(index([2]), signatories)

