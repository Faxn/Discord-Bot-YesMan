import argparse
import logging
import asyncio
import time
import sys

import  pytest

# Needed to find archiver in the path.
# Seems Hackish, there has to be a better way.
sys.path.append("..")
sys.path.append(".")

import archiver.archiver as archiver

#author and channel are `message id % <this constant>`
AUTHORS = 5
CHANNELS = 8

loop = asyncio.get_event_loop()
archive_backends = archiver.archive_backends

#
default_paths = dict()
default_paths['TinyDB'] = 'messages%d.json' % time.time()
default_paths['MongoDB'] = 'mongodb://localhost/testArchiver%d' % time.time()


################################################################################
# Modular Testing Functions and tools for testing archives
################################################################################

def gen_messages(number):
    "Generator to provide test messages"
    for i in range(number):
        yield {'id': i ,"content": "message %d" % i, 'author': {"id": i%AUTHORS}, 'channel_id': i%CHANNELS }

async def get_all_messages(archive):
    async for m in archive.get_messages():
        print(m)

async def verify_authors(archive, message_count):
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
        assert a_count >= message_count/AUTHORS - AUTHORS
    #make sure we didn't miss any messages.
    assert t_count == message_count, "%s != %s" % (t_count, args.test_count)

async def verify_channels(archive, message_count):
    t_count = 0
    for c in range(CHANNELS):
        # counter for this Channel
        c_count = 0
        async for m in archive.get_messages(channel={'id':c}):
            assert m['channel_id'] == c
            t_count += 1
            c_count += 1
        assert c_count >= message_count/CHANNELS - CHANNELS
        
    #make sure we didn't miss any messages.
    assert t_count == message_count, "%s != %s" % (t_count, args.test_count)

################################################################################
# Actual Test
################################################################################

@pytest.mark.parametrize("backend, message_count", [
    ("MongoDB", 10),
    ("TinyDB", 10)])
def test_backend(backend, message_count):
    print("Testing %s archive backend:" % backend)
    #TODO: Break this out into a fixture
    archive = archive_backends[backend](default_paths[backend])
    try:
        #TODO: Break these up into individual tests.
        insert_start = time.clock()
        f = archive.add_messages(gen_messages(message_count), all_new=True)
        loop.run_until_complete(f)
        insert_finish = time.clock()

        read_start = time.clock()
        loop.run_until_complete(get_all_messages(archive))
        read_finish = time.clock()
        
        verify_start = time.clock()
        loop.run_until_complete(verify_channels(archive, message_count))
        loop.run_until_complete(verify_authors(archive, message_count))
        verify_finish = time.clock()
        
        print( "Inserted %d records in %f clock" % (message_count, insert_finish-insert_start))
        print( "Read     %d records in %f clock" % (message_count, read_finish-read_start))
        print( "Verify   %d records in %f clock" % (message_count, verify_finish-verify_start))

    finally:
        archive.drop()

################################################################################
# Main for running manual tests.
################################################################################


if __name__ == "__main__":
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
    
    test_backend(args.test_class, args.test_count)
