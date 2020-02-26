# Per poter maneggiare il db, abbiamo bisogno dei modelli,
# che ne rispecchiano l'esatta conformazione.
# In questo caso le tabelle con annesso il metodo asDict,
# sono quelle relative ai questionari. Sono le query ai 
# questionari, infatti, che devono essere restituite dalle api
# in forma di stringa.

from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=True, unique=True)
    password = db.Column(db.String, nullable=True, default='https://shmector.com/_ph/4/184260380.png')
    status = db.Column(db.String, nullable=False, default='active')
    questionari = db.relationship('Questionario', backref='author', lazy=True)

class Questionario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titolo = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),  nullable=False)
    domande = db.relationship('Domanda', backref='questionario', lazy=True)

    def asDict(self):
        return { 'id' : self.id,
                 'titolo' : self.titolo,
                 'user_id' : self.user_id
                }

class Domanda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domanda = db.Column(db.String, nullable=False)
    questionario_id = db.Column(db.Integer, db.ForeignKey('questionario.id'),  nullable=False)
    risposte = db.relationship('Risposta', backref='domanda', lazy=True)

    def asDict(self):
        return { 'id' : self.id,
                 'domanda' : self.domanda,
                 'questionario_id' : self.questionario_id
                }

class Risposta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    risposta = db.Column(db.String, nullable=False)
    esatta = db.Column(db.Boolean, nullable=False)
    domanda_id = db.Column(db.Integer, db.ForeignKey('domanda.id'),  nullable=False)

    def asDict(self):
        return { 'id' : self.id,
                 'risposta' : self.risposta,
                 'esatta' : self.esatta,
                 'domanda_id' : self.domanda_id
                }