# db.py
from pymongo import MongoClient
import gridfs
import mongoengine as me

def init_db(app):
    uri = app.config['MONGO_URI']
    client = MongoClient(uri)
    # This line extracts the database name from the MongoDB URI.
    # It splits the URI string at the last '/' character and takes the part after it as the database name.
    # If there is no '/' in the URI, it defaults to 'venom'.
    dbname = uri.rsplit('/', 1)[-1] if '/' in uri else 'venom'
    db = client[dbname]

    # GridFS bucket wrapper
    fs = gridfs.GridFS(db)

    # ensure index to speed metadata lookups
    try:
        db.fs.files.create_index([('metadata.user_id', 1)])
    except Exception:
        pass

    # connect mongoengine (for models)
    me.connect(db=dbname, host=uri)
    return client, db, fs
