from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
import requests


app = Flask(__name__)

client = MongoClient('mongodb://iqbalmp:iqbalmp@ac-azgceyx-shard-00-00.ligsrx6.mongodb.net:27017,ac-azgceyx-shard-00-01.ligsrx6.mongodb.net:27017,ac-azgceyx-shard-00-02.ligsrx6.mongodb.net:27017/?ssl=true&replicaSet=atlas-144b7i-shard-0&authSource=admin&retryWrites=true&w=majority')
db = client.dbsparta_plus_week2


@app.route('/')
def main():
    words_result = db.words.find({}, {'_id': False})
    words = []
    
    for word in words_result:
        definition = word['definitions'][0]['shortdef']
        definition = definition if type(definition) is str else definition[0]
        words.append({
            'word': word['word'],
            'definition': definition,
        })
    return render_template(
        'index.html',
        words=words
    )

@app.route('/detail/<keyword>')
def detail(keyword):
    api_key = 'd329b7ac-6242-4c5c-b5dd-24c5ea9652a8'
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    
    response = requests.get(url)
    definitions = response.json()
    if not definitions:
        return redirect(url_for(
            'main',
            msg=f'Could not find {keyword}'
        ))

    if type(definitions[0]) is str:
        return redirect(url_for(
            'main',
            msg=f'Could not find {keyword}, did you mean {", ".join(definitions)}?'
        ))
    return render_template(
        'detail.html',
        word=keyword,
        definitions=definitions,
        status=request.args.get('status_give', 'new')
    )

@app.route('/api/save_word', methods=['POST'])
def save_word():
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions = json_data.get('definitions_give')
    doc = {
        'word': word,
        'definitions': definitions,
    }
    db.words.insert_one(doc)
    return jsonify({
        'result': 'success',
        'msg': f'the word, {word}, was saved!!!',
    })


@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    word = request.form.get('word_give')
    db.words.delete_one({'word': word})
    return jsonify({
        'result': 'success',
        'msg': f'the word {word} was deleted'
    })

@app.route('/api/get_exs', methods=['GET'])
def get_exs(): 
    word = request.args.get('word')
    data = db.sentences.find({'word': word})
    examples = []
    for example in data:
        examples.append({
            'example': example.get('example'),
            'id': str(example.get('_id')),
        })
    return jsonify({'result': 'success', 'examples' : examples})

@app.route('/api/save_ex', methods=['POST'])
def save_ex():
    example = request.form.get('example')
    word = request.form.get('word')

    doc = {
        'word': word,
        'example' : example,
    }
    db.sentences.insert_one(doc)

    return jsonify({'result': 'success',
                    'msg' : f'your sentece {example} was saved'
                    })


@app.route('/api/delete_ex', methods=['POST'])
def delete_ex():
    id = request.form.get('id')
    word = request.form.get('word')
    db.sentences.delete_one({'_id': (id)})
    return jsonify({'result': 'success'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)