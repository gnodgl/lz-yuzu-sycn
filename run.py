import sys
from tasks.lz_sync import main as lz_sync

if __name__ == '__main__':
    action = sys.argv[1]
    eval('%s()' % action)
