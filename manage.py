from app import app, db

def init_db():
    with app.app_context():
        pass

if __name__ == '__main__':
    init_db()