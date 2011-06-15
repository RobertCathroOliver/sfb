query/players
function(doc) {

    if (doc['*type'] == 'player') {
	emit(['user', doc.owner.substr(8)], doc);
	emit(['g', doc.game.substr(8)], doc);
    }
}

query/users
function(doc) {
    if (doc['*type'] == 'user') {
	emit(doc._id, doc);
    }
}

query/games
function(doc) {
    if (doc['*type'] == 'game') {
	emit(doc._id, doc);
    }
}

login/by_name
function(doc) {
    if (doc['*type'] == 'user') {
	emit(doc.name, doc)
    }
}
