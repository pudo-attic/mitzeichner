from flask import render_template, request
from core import app, db
from re import split

@app.route('/')
def index():
    q = request.args.get('q', '')
    name_parts = [p.lower() for p in split(r"[\.,\s]", q) if len(p)]
    results = []
    if len(name_parts):
        query_part = ' AND '.join(['name LIKE ?'] * len(name_parts))
        query = "SELECT * FROM signatories WHERE %s ORDER BY name, location LIMIT 100" % query_part
        name_parts = map(lambda p: "%%%s%%" % p, name_parts)
        cur = db().cursor()
        rs = cur.execute(query, name_parts)
        keys = [c[0] for c in rs.description]
        results = []
        for r in rs:
            results.append(dict(zip(keys, r)))
        cur.close()
    return render_template('index.html', q=q, results=results)

if __name__ == "__main__":
    app.debug = True
    app.run()

