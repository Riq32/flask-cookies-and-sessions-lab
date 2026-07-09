#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, session
try:
    from flask_migrate import Migrate
except Exception:
    # Provide a lightweight fallback if flask_migrate isn't available
    class Migrate:
        def __init__(self, app, db):
            # no-op fallback for environments without flask-migrate
            pass

from models import db, Article, User, ArticleSchema, UserSchema

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/clear')
def clear_session():
    session['page_views'] = 0
    return {'message': '200: Successfully cleared session data.'}, 200

@app.route('/articles')
def index_articles():
    articles = [ArticleSchema().dump(a) for a in Article.query.all()]
    return make_response(articles)

@app.route('/articles/<int:id>')
def show_article(id):
    # Track how many articles this user has viewed in their session.
    # session.get(..., 0) means the very first request initializes the
    # counter at 0 before we increment it below.
    session['page_views'] = session.get('page_views', 0) + 1

    if session['page_views'] <= 3:
        article = Article.query.filter(Article.id == id).first()
        article_json = ArticleSchema().dump(article)
        return make_response(article_json, 200)
    else:
        return make_response(
            {'message': 'Maximum pageview limit reached'}, 401
        )


if __name__ == '__main__':
    app.run(port=5555)