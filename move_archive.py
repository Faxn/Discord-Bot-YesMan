import argparse
import logging
import asyncio

import archiver.archiver as archiver

class dumpArchive(archiver.Archive):
    DEFAULT_PATH = "-"
    def __init__(self, path, loop=None):
        pass

    def add_messages(self, messages, all_new=False):
        for m in messages:
            print(m)

archive_backends = archiver.archive_backends
archive_backends['dump'] = dumpArchive

parser = argparse.ArgumentParser(description='move')
parser.add_argument('--debug', action='store_true', default=True)
parser.add_argument('in_class', action='store', choices=archive_backends)
parser.add_argument('--in_path', '-i', action='store', default='-')
parser.add_argument('out_class', action='store', choices=archive_backends)
parser.add_argument('--out_path', '-o', action='store', default="-")
args = parser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

logging.info('args: %s', args)
logging.info('backends: %s', archive_backends)

if(args.in_path == '-'):
    args.in_path = default_paths[args.in_class]
if(args.out_path == '-'):
    args.out_path = default_paths[args.out_class]

in_archive = archive_backends[args.in_class](args.in_path)
out_archive = archive_backends[args.out_class](args.out_path)

f = out_archive.async_add_messages(in_archive.get_all_messages())
asyncio.get_event_loop().run_until_complete(f)
