from . import app
import os
import json
import pymongo
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401
from pymongo import MongoClient
from bson import json_util
from pymongo.errors import OperationFailure
from pymongo.results import InsertOneResult
from bson.objectid import ObjectId
import sys
from urllib.parse import quote_plus

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "songs.json")
songs_list: list = json.load(open(json_url))

# client = MongoClient(
#     f"mongodb://{app.config['MONGO_USERNAME']}:{app.config['MONGO_PASSWORD']}@localhost")
mongodb_service = os.environ.get('MONGODB_SERVICE')
mongodb_username = os.environ.get('MONGODB_USERNAME')
mongodb_password = os.environ.get('MONGODB_PASSWORD')
mongodb_port = os.environ.get('MONGODB_PORT')

print(f'The value of MONGODB_SERVICE is: {mongodb_service}')

if mongodb_service == None:
    app.logger.error('Missing MongoDB server in the MONGODB_SERVICE variable')
    # abort(500, 'Missing MongoDB server in the MONGODB_SERVICE variable')
    sys.exit(1)

if mongodb_username and mongodb_password:
    address = mongodb_service if ':' in mongodb_service else f"{mongodb_service}:{mongodb_port or '27017'}"
    url = f"mongodb://{quote_plus(mongodb_username)}:{quote_plus(mongodb_password)}@{address}"
else:
    address = mongodb_service if ':' in mongodb_service else f"{mongodb_service}:{mongodb_port or '27017'}"
    url = f"mongodb://{address}"


# Do not log the MongoDB URL because it can contain credentials.

try:
    client = MongoClient(url, serverSelectionTimeoutMS=5000)
except OperationFailure as e:
    app.logger.error(f"Authentication error: {str(e)}")

db = client.songs
db.songs.create_index('id', unique=True)
if db.songs.count_documents({}) == 0:
    db.songs.insert_many(songs_list)

def parse_json(data):
    return json.loads(json_util.dumps(data))

######################################################################
# INSERT CODE HERE
######################################################################

@app.route('/health')
def health():
    client.admin.command('ping')
    return jsonify(status='OK'), 200

@app.route('/count')
def count():
    return jsonify(length=db.songs.count_documents({})), 200

@app.route('/song', methods=['GET'])
def get_songs():
    return jsonify(list(db.songs.find({}, {'_id': 0}))), 200

@app.route('/song/<int:id>', methods=['GET'])
def get_song(id):
    song = db.songs.find_one({'id': id}, {'_id': 0})
    if song is None:
        abort(404)
    return jsonify(song), 200

def song_payload(id=None):
    song = request.get_json()
    if not isinstance(song, dict) or not isinstance(song.get('id', id), int):
        abort(400, description='A song object with an integer id is required')
    if id is not None and song.get('id', id) != id:
        abort(400, description='Song id must match the URL')
    song.pop('_id', None)
    return song

@app.route('/song', methods=['POST'])
def create_song():
    from pymongo.errors import DuplicateKeyError
    song = song_payload()
    try:
        db.songs.insert_one(song.copy())
    except DuplicateKeyError:
        return jsonify(Message=f"song with id {song['id']} already present"), 302
    response = jsonify(song)
    response.status_code = 201
    response.headers['Location'] = url_for('get_song', id=song['id'])
    return response

@app.route('/song/<int:id>', methods=['PUT'])
def update_song(id):
    song = song_payload(id)
    song['id'] = id
    result = db.songs.update_one({'id': id}, {'$set': song})
    if result.matched_count == 0:
        abort(404)
    return jsonify(db.songs.find_one({'id': id}, {'_id': 0})), 200

@app.route('/song/<int:id>', methods=['DELETE'])
def delete_song(id):
    if db.songs.delete_one({'id': id}).deleted_count == 0:
        abort(404)
    return '', 204
