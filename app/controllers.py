from flask import jsonify, request
from app import db, app, api
from flask_restplus import Resource, fields, reqparse
import traceback
from app.models import Questionario, Domanda, Risposta

# In questo caso il namespace acui sono associati gli endpoint si chiama quizs.
# L'url base ell'api è della forma : dominio + api/v1.0/quizs

quizs = api.namespace('api/v1.0/quizs',description='CRUD operation for quizs')

# Essendo le tabelle più di una e le relazioni tra di esse uno a molti,
# abbiamo bisogno di più modelli a richiedere. Prova

titoloModel = quizs.model('titoloModel', {
    'titolo' : fields.String(required=True, validate=True)
    }
)

domandaModel = quizs.model('domandaModel', {
    'domanda' : fields.String(required=True, validate=True)
    }
)

rispostaModel = quizs.model('rispostaModel', {
    'risposta' : fields.String(required=True, validate=True),
    'esatta' : fields.Boolean(required=True, validate=True)
    }
)

parserId = reqparse.RequestParser()
parserId.add_argument('questionario_id',type=int)

# Primo endpoint: richieste generali sui quiz anche senza autenticazione:
# GET:
#   fornisce tutti i quiz disponibili, o uno solo,
#   in caso si fornisca l'id del quiz.

@quizs.route('')
class General_quizs_requests(Resource):
    @quizs.expect(parserId)
    def get(self):
        '''get all quizs or one'''
        questionario_id = request.args.get('questionario_id')
        if not questionario_id:
            quizs = Questionario.query.all()
            response={}
            response['data']=[]
            for quiz in quizs:
                response['data'].append(quiz.asDict())
            return jsonify(response)
        quiz = Questionario.query.get(questionario_id)
        if not quiz:
           return 'Quiz Not Found', 404
        response = {}
        response['titolo'] = quiz.titolo
        response['domande'] = {}
        for domanda in quiz.domande:
            response['domande'][domanda.domanda] = {}
            for risposta in domanda.risposte:
                response['domande'][domanda.domanda][risposta.risposta] = risposta.esatta
        return jsonify(response)

# Secondo endpoint: richieste sui quiz di un utente autenticato
# POST:
#   l'utente può creare un quiz una volta autenticato.
#   La prima fase di creazione del quiz richiederà la scelta di un titolo.
# GET:
#   possono essere rilevati tutti i quiz creati da un singolo utente.

@quizs.route('/<int:user_id>')
class User_quizs_requests(Resource):
    @quizs.expect(titoloModel, validate=True)
    def post(self,user_id):
        '''create a new quiz'''
        #create a new record in the DB
        data = request.get_json()
        titolo = data.get("titolo")
        quiz = Questionario(titolo=titolo, user_id=user_id)
        db.session.add(quiz)
        db.session.commit()
        return jsonify(quiz.asDict())

    def get(self,user_id):
        '''get all quizs from a user'''
        quizs = Questionario.query.filter_by(user_id=user_id).all()
        if not quizs:
            'This user does not own any quizs', 400
        response = {}
        for quiz in quizs:
            response[quiz.id] = quiz.titolo
        return jsonify(response)

# Terzo Endpoint: richieste relative ad un singolo quiz, accessibili
#   una volta creato.
# POST: consente di creare una domanda del quiz.
# GET: consente di prelevare tutte le informazioni di un singolo quiz.
#   ( inclusi gli id di domande e risposte ). E necessario inserire anche l'id
#   dell'autore del quiz.
# DELETE: cancella il quiz e le domande e risposte ad esso annesso.
# PUT: modifica il titolo di un quiz.

@quizs.route('/<int:user_id>/<int:questionario_id>')
class Single_quiz_requests(Resource):
    @quizs.expect(domandaModel, validate=True)
    def post(self,user_id,questionario_id):
        '''create a new question'''
        quiz = Questionario.query.get(questionario_id)
        if not quiz:
                return 'quiz not in DB', 404
        data = request.get_json()
        domanda = data.get("domanda")
        d = Domanda(domanda=domanda,questionario_id=questionario_id)
        db.session.add(d)
        db.session.commit()
        return jsonify(d.asDict())

    def get(self,user_id,questionario_id):
        '''get a quiz from a user'''
        quiz = Questionario.query.get(questionario_id)
        if not quiz:
           return 'Quiz Not Found', 404
        if quiz.user_id != user_id:
           return 'This quiz is not by this user', 400
        response = {}
        response['titolo'] = quiz.titolo
        response['domande'] = {}
        for domanda in quiz.domande:
            response['domande'][domanda.id] = {domanda.domanda : {}}
            for risposta in domanda.risposte:
                response['domande'][domanda.id][domanda.domanda][risposta.id] = [risposta.risposta,risposta.esatta]
        return jsonify(response)

    def delete(self,user_id, questionario_id):
        '''deletes a quiz'''
        try:
            q = Questionario.query.filter_by(id = questionario_id).first()
            if (q is None):
                return 'questionario not found', 404
            if q.user_id != user_id:
                return 'You cannot delete someone else Quiz', 403
            for domanda in q.domande:
                for risposta in domanda.risposte:
                    db.session.delete(risposta)
                db.session.delete(domanda)
            db.session.delete(q)
            db.session.commit()
            return  'Quiz Deleted', 204
        except:
            return 'Error server side', 500

    @quizs.expect(titoloModel, validate=True)
    def put(self,user_id,questionario_id):
        '''update a quiz title'''
        try:
            data = request.get_json()
            titolo = data.get("titolo")
            #checking if quiz exists
            q = Questionario.query.get(questionario_id)
            if(q is None):
                return 'quiz not in DB', 404
            if q.user_id != user_id:
                return 'you are not allowed to modifie this quiz', 403
            q.titolo = titolo if titolo else q.titolo
            db.session.commit()
            return jsonify(q.asDict())
        except:
            app.logger.error(traceback.format_exc())
            return 'Error server side', 500

# Quarto Endpoint: richieste relative ad una singola domanda di un quiz.
#   Accessibili una volta creata la domanda.
# POST: consente di creare una risposta alla domanda.
# PUT: modifica il testo della domanda
# DELETE: cancella la domande e risposte ad essa annessa.

@quizs.route('<int:user_id>/<int:questionario_id>/<int:domanda_id>')
class Single_question_requests(Resource):
    @quizs.expect(rispostaModel, validate=True)
    def post(self,user_id,questionario_id,domanda_id):
        '''create a new answer'''
        quiz = Questionario.query.get(questionario_id)
        domanda = Domanda.query.get(domanda_id)
        if not quiz or not domanda:
                return 'quiz or question not in DB', 404
        data = request.get_json()
        risposta = data.get("risposta")
        esatta = data.get("esatta")
        r = Risposta(risposta=risposta,esatta=esatta,domanda_id=domanda_id)
        db.session.add(r)
        db.session.commit()
        return jsonify(r.asDict())

    @quizs.expect(domandaModel, validate=True)
    def put(self,user_id,questionario_id,domanda_id):
        '''update a quiz question'''
        try:
            q = Questionario.query.get(questionario_id)
            if(q is None):
                return 'quiz not in DB', 404
            if q.user_id != user_id:
                return 'you are not allowed to modifie this quiz', 403
            d = Domanda.query.get(domanda_id)
            if not d:
                return 'question not in DB', 404
            data = request.get_json()
            domanda = data.get("domanda")
            if d.questionario_id != questionario_id:
                return 'you are not allowed to modifie this question', 403
            d.domanda = domanda if domanda else d.domanda
            db.session.commit()
            return jsonify(d.asDict())
        except:
            app.logger.error(traceback.format_exc())
            return 'Error server side', 500

    def delete(self,user_id, questionario_id, domanda_id):
        '''deletes a question'''
        try:
            q = Questionario.query.filter_by(id = questionario_id).first()
            if (q is None):
                return 'Quiz not found', 404
            if q.user_id != user_id:
                return "You cannot delete questions from someone else's quiz", 403
            d = Domanda.query.get(domanda_id)
            if d.questionario_id != questionario_id:
                return "You cannot delete questions from a different quiz", 403
            for risposta in d.risposte:
                db.session.delete(risposta)
            db.session.delete(d)
            db.session.commit()
            return  'Question Deleted', 204
        except:
            return 'Error server side', 500

# Quinto Endpoint: richieste relative ad una singola risposta ad una domanda di un quiz.
#   Accessibili una volta creata la risposta.
# PUT: modifica il testo della risposta.
#   Una volta modificato il testo, è necessario specificare nuovamente
#   se la risposta è esatta o meno.
# DELETE: cancella la risposta.

@quizs.route('<int:user_id>/<int:questionario_id>/<int:domanda_id>/<int:risposta_id>')
class Single_answer_requests(Resource):
    @quizs.expect(rispostaModel, validate=True)
    def put(self,user_id,questionario_id,domanda_id,risposta_id):
        '''update a quiz answer'''
        try:
            q = Questionario.query.get(questionario_id)
            if(q is None):
                return 'quiz not in DB', 404
            if q.user_id != user_id:
                return 'you are not allowed to modifie this quiz', 403
            r = Risposta.query.get(risposta_id)
            if not r:
                return 'answer not in DB', 404
            if r.domanda_id != domanda_id:
                 return 'you are not allowed to modifie this answer', 403
            data = request.get_json()
            risposta = data.get("risposta")
            esatta = data.get("esatta")
            esatta = str(esatta)
            r.risposta = risposta if risposta else r.risposta
            r.esatta = True if esatta == 'True' else False
            db.session.commit()
            return jsonify(r.asDict())
        except:
            app.logger.error(traceback.format_exc())
            return 'Error server side', 500

    def delete(self,user_id, questionario_id, domanda_id, risposta_id):
        '''deletes an answer'''
        try:
            q = Questionario.query.filter_by(id = questionario_id).first()
            if (q is None):
                return 'Quiz not found', 404
            if q.user_id != user_id:
                return "You cannot delete answers from someone else's quiz", 403
            d = Domanda.query.get(domanda_id)
            if not d:
                return 'Question not found', 404
            if d.questionario_id != questionario_id:
                return "You cannot delete answers from a different quiz", 403
            r = Risposta.query.get(risposta_id)
            if not r:
                return 'Answer not found', 404
            db.session.delete(r)
            db.session.commit()
            return  'Answer Deleted', 204
        except:
            return 'Error server side', 500
