import argparse
import logging
import asyncio
import time

import archiver.archiver as archiver


loop = asyncio.get_event_loop()
archive_backends = archiver.archive_backends

#
default_paths = dict()
default_paths['TinyDB'] = 'messages%d.json' % time.time()
default_paths['MongoDB'] = 'mongodb://localhost/testArchiver%d' % time.time()

parser = argparse.ArgumentParser(description='move')
parser.add_argument('--debug', action='store_true', default=True)
parser.add_argument('test_class', action='store', choices=archive_backends)
parser.add_argument('test_count', type=int, default=10)
parser.add_argument('--in_path', '-i', action='store', default='-')
args = parser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

def test_messages(number):
    for i in range(number):
        yield {'id': i ,"content": "message %d" % i}

archive = archive_backends[args.test_class](default_paths[args.test_class])

insert_start = time.clock()
f = archive.async_add_messages(test_messages(args.test_count))
loop.run_until_complete(f)
insert_finish = time.clock()

read_start = time.clock()
for m in archive.get_all_messages():
    print(m)
read_finish = time.clock()

print( "Inserted %d records in %f clock" % (args.test_count, insert_finish-insert_start))
print( "Read     %d records in %f clock" % (args.test_count, read_finish-read_start))



if args.test_class == 'MongoDB':
    import motor.motor_asyncio
    import re
    client = motor.motor_asyncio.AsyncIOMotorClient(default_paths['MongoDB'])
    f = client.database_names()
    dbs = asyncio.get_event_loop().run_until_complete(f)
    for db in dbs:
            if re.match("^testArchiver", db):
                f2 = client.drop_database(db)
                asyncio.get_event_loop().run_until_complete(f2)
    
