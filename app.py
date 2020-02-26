# Questo è un microservizio per le operazioni CRUD sulle tabelle,
# relative ai questionari, realizzate nel microservizio Users.

from app import app

if __name__ == '__main__':
    app.run(debug=True)