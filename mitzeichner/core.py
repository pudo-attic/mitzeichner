import sys
from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy
from sqlalchemy import or_

app = Flask('mitzeichner')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/mitzeichner'
app.config['SQLALCHEMY_POOL_SIZE'] = 25
app.secret_key = 'hasenbaeren'
db = SQLAlchemy(app)

class Mitzeichner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    petition_id = db.Column(db.String(20), index=True)
    signer_id = db.Column(db.String(255))
    theme = db.Column(db.String(2000), index=True)
    title = db.Column(db.String(2000), index=True)
    creator = db.Column(db.String(2000))
    end_date = db.Column(db.String(255))
    name = db.Column(db.String(2000), index=True)
    location = db.Column(db.String(2000), index=True)
    sign_date = db.Column(db.String(100))

    def __init__(self, petition_id, signer_id, theme, title, creator,
            end_date, name, location, sign_date):
        self.petition_id = petition_id
        self.signer_id = signer_id
        self.theme = theme
        self.title = title
        self.creator = creator
        self.end_date = end_date
        self.name = name
        self.location = location
        self.sign_date = sign_date

    @classmethod
    def by_petition_signer(cls, petition_id, signer_id):
        return cls.query.filter_by(petition_id=petition_id)\
                .filter_by(signer_id=signer_id).first()
    
    @classmethod
    def themes(cls):
        return db.session.query(cls.theme).distinct().all()

    def __repr__(self):
        return "Mitzeichnung<%s,%s>" % (self.name.encode('utf-8'),
                                        self.title.encode('utf-8'))


class Delegation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String(2000), index=True)
    agent_name = db.Column(db.String(2000))
    agent_location = db.Column(db.String(2000))
    username = db.Column(db.String(2000))
    password = db.Column(db.String(2000))
    
    def __init__(self, theme, agent_name, agent_location, 
                 username, password):
        self.theme = theme
        self.agent_name = agent_name
        self.agent_location = agent_location
        self.username = username
        self.password = password

    @classmethod
    def by_theme_name(cls, theme, name, location):
        q = cls.query.filter(cls.agent_name==name)
        q = q.filter(cls.agent_location==location)
        q = q.filter(or_(cls.theme == '*', cls.theme==theme))
        return q.all()


if __name__ == '__main__':
    if not len(sys.argv) == 2:
        raise ValueError("Need to give a command: createdb")
    if sys.argv[1] == 'createdb':
        db.create_all()


