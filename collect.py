import docker, pymongo
import threading

def collect(db, clt, Id):
	try:
		db.dockercontainers.insert_one(clt.inspect_container(Id))
	except Exception as e:
		print(e)
	count = 0
	for stat in clt.stats(Id, decode=True):
		count += 1
		stat['Id'] = Id
		db.dockerstats.insert_one(stat)
		print(Id, count)

def eventListner(clt, status_handlers):
	for event in clt.events(decode=True):
		print(event)
		status = event['status']
		if status in status_handlers:
			status_handlers[status](event)

def main(clt, db):
	db.dockercontainers.create_index([('Id', pymongo.ASCENDING)], unique=True)
	db.dockerstats.create_index([('read', pymongo.ASCENDING), ('Id', pymongo.ASCENDING)], unique=True)
	def spawn_worker(Id):
		t = threading.Thread(target=collect, args=(db, clt, Id))
		t.daemon = True
		t.start()
	def on_start(event):
		spawn_worker(event['id'])
	status_handlers = { 'start' : on_start }
	for container in clt.containers():
		spawn_worker(container['Id'])
	eventListner(clt, status_handlers)

if __name__ == '__main__':
	import os
	base_url = None
	tls_config = False
	if 'DOCKER_CERT_PATH' in os.environ and 'DOCKER_HOST' in os.environ:
		DOCKER_HOST = os.environ['DOCKER_HOST']
		DOCKER_CERT_PATH = os.environ['DOCKER_CERT_PATH']
		verify = os.path.join(DOCKER_CERT_PATH,'ca.pem')
		client_cert = (os.path.join(DOCKER_CERT_PATH,'cert.pem'),os.path.join(DOCKER_CERT_PATH,'key.pem'))
		tls_config = docker.tls.TLSConfig(assert_hostname=False, verify=verify, client_cert=client_cert)
		base_url = 'https://' + DOCKER_HOST.split('//')[1]
	main(docker.Client(base_url=base_url,tls=tls_config), pymongo.MongoClient()['default'])
