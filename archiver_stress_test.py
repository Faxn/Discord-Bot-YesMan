import argparse
import logging
import asyncio
import time

import archiver.archiver as archiver


#author and channel are dreived from `message id % <this constant>`
AUTHORS = 5
CHANNELS = 8

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
        yield {'id': i ,"content": "message %d" % i, 'author': {"id": i%AUTHORS}, 'channel_id': i%CHANNELS }

archive = archive_backends[args.test_class](default_paths[args.test_class])

async def archiver_test():
    async for m in archive.get_messages():
        print(m)






async def verify():
    """Verify that the query criteria on get_messages work correctly."""
    
    # total count, count all the messages we read
    t_count = 0 
    for a in range(AUTHORS):
        # count for this author
        a_count = 0
        async for m in archive.get_messages(user={'id':a}):
            assert m['author']['id'] == a, "%s != %s" % (m['author']['id'], a)
            t_count += 1
            a_count += 1
        #make sure mesages for this author are within expected limits.
        assert a_count >= args.test_count/AUTHORS - AUTHORS
    #make sure we didn't miss any messages.
    assert t_count == args.test_count, "%s != %s" % (t_count, args.test_count)
    
    t_count = 0
    for c in range(CHANNELS):
        # counter for this Channel
        c_count = 0
        async for m in archive.get_messages(channel={'id':a}):
            assert m['author']['id'] == a
            t_count += 1
            c_count += 1
        assert c_count >= args.test_count/CHANNELS - CHANNELS
        
    #make sure we didn't miss any messages.
    assert t_count == args.test_count, "%s != %s" % (t_count, args.test_count)
    
try:
    insert_start = time.clock()
    f = archive.async_add_messages(test_messages(args.test_count))
    loop.run_until_complete(f)
    insert_finish = time.clock()

    read_start = time.clock()
    loop.run_until_complete(archiver_test())
    read_finish = time.clock()

    loop.run_until_complete(verify())
    
    print( "Inserted %d records in %f clock" % (args.test_count, insert_finish-insert_start))
    print( "Read     %d records in %f clock" % (args.test_count, read_finish-read_start))

finally:
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
        
