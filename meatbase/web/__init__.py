from flask import Flask, render_template, jsonify, request
import rethinkdb
import HTMLParser


dbconn = rethinkdb.connect('localhost', 28015)

# Start Flask application
app = Flask(__name__)

@app.route("/monster/name/<monster_name>")
def monster_name(monster_name):
	result = rethinkdb.db('kol').table('monsters').filter(rethinkdb.row['name'].match('^(?i)' + monster_name +'$')).run(dbconn)
	monster = None
	try:
		monster = list(result)[0]
	except:
		pass
	drop_results = []
	if monster:
		for drop in monster['drops']:
			drop_name = drop.split(' (')[0]
			drop_row = rethinkdb.db('kol').table('items').filter(rethinkdb.row['name'].match('^(?i)' + drop_name +'$')).run(dbconn)
			for d in drop_row:
				drop_results.append(d)
	params = {
		"result": monster,
		"drop_results": drop_results
	}
	return render_template('monster.html', **params)

@app.route("/zone/<zone_id>")
def zone(zone_id):
	result = rethinkdb.db('kol').table('zones').get(zone_id).run(dbconn)
	params = {
		"result": result
	}
	return render_template('zone.html', **params)

@app.route("/item/<int:item_id>")
def item(item_id):
	result = rethinkdb.db('kol').table('items').get(item_id).run(dbconn)
	desc_result = rethinkdb.db('kol').table('descs').get(result['descId']).run(dbconn)
	drops_from = rethinkdb.db('kol').table('monsters').filter(lambda m: m["drops"].contains(lambda drop: drop.match(result['name']))).run(dbconn)
	if desc_result:
		result['desc'] = desc_result['desc']
	params = {
		"result": result,
		"drops_from": drops_from
	}
	return render_template('item.html', **params)

@app.route("/search")
def search():
	q = request.args.get('q')
	item_results = list(rethinkdb.db('kol').table('items').filter(rethinkdb.row['name'].match('(?i)' + q)).limit(10).run(dbconn))
	zone_results = list(rethinkdb.db('kol').table('zones').filter(rethinkdb.row['name'].match('(?i)' + q)).limit(10).run(dbconn))
	params = {
		"query": q,
		"item_results": item_results,
		"zone_results": zone_results
	}
	return render_template('search.html', **params)

@app.route("/")
def index():
	return render_template('index.html')
