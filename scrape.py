from itertools import count
from lxml import html
import urllib2
from core import db

INDEX_URL = 'https://epetitionen.bundestag.de/index.php?action=petition&sa=list%s&limit=100&start=%s'
SIGN_URL = 'https://epetitionen.bundestag.de/index.php?action=petition&sa=sign&petition=%s&limit=100&start=%s'

conn = db()


def urldoc(url, *a):
    print url % a
    fh = urllib2.urlopen(url % a)
    doc = html.parse(fh)
    fh.close()
    return doc


def index():
    for list_ in range(2,5):
        last_set = set()
        for i in count():
            page = set()
            doc = urldoc(INDEX_URL, list_, i*100)
            for row in doc.findall('//tr'):
                cols = list(row.findall('.//td'))
                if len(cols) != 6:
                    continue
                id, title, creator, end_date, s_count, forum = cols
                theme, title = title.xpath('string()').split(' - ', 1)
                signatories(id.text,
                            theme, title,
                            creator.text, 
                            end_date.text)
                page.add(id.text)
            print page
            if last_set.intersection(page) == page:
                break
            last_set = page

def signatories(id, theme, title, creator, end_date):
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

def persist(petition_id, signer_id, theme, title, creator, end_date, name,
        location, sign_date):
    c = conn.cursor()
    cur = c.execute("""SELECT petition_id, signer_id FROM signatories WHERE
           petition_id = ? AND signer_id = ?""", (petition_id, signer_id))
    if not cur.fetchone():
        c.execute("""INSERT INTO signatories VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (petition_id, signer_id, theme, title, creator, end_date, name,
                location, sign_date))
        conn.commit()
    c.close()

if __name__ == '__main__':
    try:
        cur = conn.cursor() 
        cur.execute("""CREATE TABLE signatories (
                petition_id,
                signer_id,
                theme,
                title,
                creator,
                end_date,
                name,
                location,
                sign_date)""")
        conn.commit()
        cur.close()
    except Exception, e:
        pass
    index()

