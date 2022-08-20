#!/usr/bin/env python

# Visit https://github.com/rqlite/pyrqlite to install Python client library.
import argparse
import pyrqlite.dbapi2 as dbapi2

def index_logs(file, host, port):
	# Connect to the rqlite database.
	connection = dbapi2.connect(
    	host=host,
    	port=port,
	)

	# Open the file containing the data to be indexed.
	logs = open(file, 'r')

	# Get a cursor, and creating the full-text search table.
	cursor = connection.cursor()
	cursor.execute('CREATE VIRTUAL TABLE logs USING fts4(entry)')

	# Index the data. Use Queued Writes for greater write performance. See
	# https://github.com/rqlite/rqlite/blob/master/DOC/QUEUED_WRITES.md for
	# more details about Queued Writes.
	for entry in logs:
		cursor.execute(sql, (entry.strip(),), queue=True)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="index log data using rqlite")
	parser.add_argument('file', metavar='FILE', type=str, help='path to log file')
	parser.add_argument('--host', type=str, default='localhost', help='rqlite host')
	parser.add_argument('--port', type=int, default=4001, help='rqlite port')
	args = parser.parse_args()

	index_logs(args.file, args.host, args.port)
