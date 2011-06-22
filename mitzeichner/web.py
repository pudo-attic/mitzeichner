import colander
from flask import render_template, request, redirect, flash
from core import app, db, Mitzeichner, Delegation
from delegation import check_credentials
from re import split

class DelegationForm(colander.MappingSchema):
    agent_name = colander.SchemaNode(colander.String())
    agent_location = colander.SchemaNode(colander.String())
    theme = colander.SchemaNode(colander.String())
    username = colander.SchemaNode(colander.String())
    password = colander.SchemaNode(colander.String())

@app.route('/delegate', methods=['POST'])
def delegate():
    try:
        data = DelegationForm().deserialize(request.form)
        #if not check_credentials(data.get('username'), data.get('password')):
        #    flash("Deine Anmeldedaten sind inkorrekt.")
        #else:
        delegation = Delegation(data.get('agent_name'),
                                data.get('agent_location'),
                                data.get('theme'),
                                data.get('username'),
                                data.get('password'))
        db.session.add(delegation)
        db.session.commit()
        flash("Deine Delegation wurde eingerichtet. " +
              "Widerruf kommt in Version 2" )
    except colander.Invalid:
        flash("Fehler in den Eingabedaten!")
    return redirect("/")


@app.route('/')
def index():
    qs = request.args.get('q', '')
    name_parts = [p.lower() for p in split(r"[\.,\s]", qs) if len(p)]
    results = []
    if len(name_parts):
        q = Mitzeichner.query
        for part in name_parts:
            q = q.filter(Mitzeichner.name.like("%%%s%%" % part))
        q = q.order_by(Mitzeichner.name.asc())
        q = q.order_by(Mitzeichner.location.asc())
        results = q.all()
    themes = map(lambda t: t[0], Mitzeichner.themes())
    return render_template('index.html', q=qs,
            themes=themes, results=results)

if __name__ == "__main__":
    app.debug = True
    app.run()

