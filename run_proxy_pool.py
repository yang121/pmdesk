import io
import sys

from proxypool.scheduler import Scheduler


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main():
    try:
        s = Scheduler()
        s.run()
    except Exception as e:
        tb = sys.exc_info()[2]
        print(e.with_traceback(tb))
        main()


if __name__ == '__main__':
    main()
