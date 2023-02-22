#!/usr/bin/env python

import argparse
import time

# Visit https://github.com/rqlite/pyrqlite to install Python client library.
import pyrqlite.dbapi2 as dbapi2

def create_table(conn):
	cursor = conn.cursor()
	cursor.execute('CREATE VIRTUAL TABLE logs USING fts4(entry)')
	cursor.close()

def drop_table(conn):
	cursor = conn.cursor()
	try:
		cursor.execute('DROP TABLE IF EXISTS logs')
	except:
		pass
	cursor.close()

def count_indexed_logs(conn):
	cursor = conn.cursor()
	cursor.execute('SELECT COUNT(*) FROM logs')
	res = cursor.fetchone()
	cursor.close()
	return res['COUNT(*)']

def expect_count(conn, n, timeout_sec):
	start = time.time()
	while True:
		c = count_indexed_logs(conn)
		if count_indexed_logs(conn) == n:
			return

		if (time.time() - start) >= timeout_sec:
			raise Exception("timeout waiting for counts to match, expected %d, got %d" % (n, c))
		time.sleep(0.1)

def index_logs(file, host, port, progress, number, check, ctimeout):
	# Connect to the rqlite database.
	connection = dbapi2.connect(host=host,port=port)

	# Open the file containing the data to be indexed.
	logs = open(file, 'r')

	# Get a cursor, and create the full-text search table.
	drop_table(connection)
	create_table(connection)

	start = time.time()

	# Index the data. Use Queued Writes for greater write performance. See
	# https://rqlite.io/docs/api/queued-writes for more details about Queued Writes.
	cursor = connection.cursor()
	sql = 'INSERT INTO logs(entry) VALUES(?)'
	n = 0
	for entry in logs:
		cursor.execute(sql, (entry.strip(),), queue=True)
		n+=1
		if n % progress == 0:
			print ("%d logs written, %d written per second" %  (n, n/(time.time() - start)))
			if check:
			    expect_count(connection, n, ctimeout)
		if n is not None and n == number:
			break

	duration = time.time() - start
	print("%d total logs indexed in %.2f seconds, %d indexed per second" % (n, duration, n/duration))

	cursor.close()
	logs.close()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Index log data using rqlite")
	parser.add_argument('file', metavar='FILE', type=str, help='path to log file')
	parser.add_argument('--host', type=str, default='localhost', help='rqlite host')
	parser.add_argument('--port', type=int, default=4001, help='rqlite port')
	parser.add_argument('--progress', metavar='P', type=int, default=5000, help='print progress every P logs')
	parser.add_argument('--number', metavar='N', type=int, default=None, help='number of entries to index')
	parser.add_argument('--check', action='store_true', help='perform correctness checks during indexing')
	parser.add_argument('--ctimeout', type=int, default=10, help='timeout in seconds for correctness check')
	args = parser.parse_args()

	index_logs(args.file, args.host, args.port, args.progress, args.number, args.check, args.ctimeout)
