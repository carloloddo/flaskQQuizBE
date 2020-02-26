# API Questionari

L'API Questionari è finalizzata alla creazione di un front-end che consenta:
- La registrazione di utenti.
- La loro autenticazione.
- La possibilità per un utente autenticato di creare un         questionario a risposta multipla o vero-falso.
- La modifica dei questionari da partedei loro autori.
- La loro eliminazione.
- La possibilità di accedere, visionare ed effettuare un        questionario da parte di qualsiasi utente.

# Struttura

La struttura di questa API è di tipo MICRO-SERVICES.
Il sistema di API infatti è diviso in 2 app.

# Users

Si occupa di mettere a disposizione degli endpoint,
dove è possibile effettuare delle richieste CRUD, sul db,relative agli Utenti.
Nonchè della creazione e strutturazione del db.

# Quizs

Si occupa di mettere a disposizione degli endpoint,
dove è possibile effettuare delle richieste CRUD, sul db,relative ai Questionari.

# Come Funziona:

Per lanciare il progetto è necessario:

- Scaricare ed estrarre il progetto.
- Aprire due terminali distinti.
- In uno dei due entrare nella cartella Users
- Nell'altro nella cartella Quizs.
- Attivare in entrambi un virtual environmant python
- Installare i requirenments presenti all'interno delle due 
    app ( in questo caso son gli stessi ).
- Avviare in entrambi i terminali i due progetti col comando:
    pytho app.py.
- Aprire un browser gli url: 
    - http://localhost:8000/
    - http://localhost:5000/

- Verificare che sia possibile attuare le richieste http in 
     entrambe le api.
- In caso ci fossero problemi col recupero dei dati:
    entrare nei due file __init__.py e sostisture
    l' url del db con il suo path generale nel vostro computer.
    Se si usa windows in questo caso bisogna ricordarsi 
    di evitare i caratteri escape ponendo una r prima della stringa:
    es. app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///C:home\..\site.db'

# N.B.
    Queste Api è in via di sviluppo.
    Non tutti gli errori sono stati previsti.
    Sono prive di test e di documentazione relativa a
    codici di ritorno.
    
