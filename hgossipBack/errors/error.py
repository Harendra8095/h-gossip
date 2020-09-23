from flask import render_template
from hgossipBack.config import DbEngine_config
from hgossipBack import create_db_engine, create_db_sessionFactory


engine = create_db_engine(DbEngine_config)
SQLSession = create_db_sessionFactory(engine)
session = SQLSession()

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    conn = session.connection()
    session.rollback()
    return render_template('500.html'), 500