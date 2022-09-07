# rqlite-fts4
Building a highly-available search engine using rqlite.

## Test data
You can download the test data set with the following command (tested on Linux):
```bash
curl https://storage.googleapis.com/bucket-vallified/rqlite/access.log.gz >fts4-access-full.log.gz
```
Decompress the data set as follows:
```bash
gunzip fts4-access-full.log.gz
```
What results is an Apache web server access log file, containing 9340622 entries.

## Indexing the log data
Use the Python program in this repository to index the data. You must have at least 1 rqlite node up and running. The indexing program assume rqlite is available at `127.0.0.1:4001`, but you can override this via command line options.
```bash
python indexer.py fts4-access-full.log
```
Pass `-h` to the program to see full options. Depending on the hardware you use for your rqlite system, it could take a few minutes to index all the log data.
