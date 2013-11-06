import couchdb

couch = couchdb.Server()

db = couch.create('test') #newlycreated
#db = couch['mydb'] # existing


doc_id, doc_rev = db.save({'type': 'Person', 'name': 'Richard Evans'})
doc = db[doc_id]
print doc['type']
print doc['name']
for id in db:
	print doc_id
	print doc_rev

db.delete(doc)
couch.delete('test')

