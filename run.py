from proxypool.scheduler import Scheduler
import sys
import io
import multiprocessing
from setting import thread
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')



def main(data):
    try:
        s = Scheduler(data)
        s.run()
    except:
        main(data)


if __name__ == '__main__':
    work_data = []
    with open("setting.json", 'r', encoding='utf8') as setting_file:
        setting_dict = eval(setting_file.read())
    for key in setting_dict:
        data = thread(key)
        work_data.append(multiprocessing.Process(target=main,args =(data,)))
    for work in work_data:
        work.start()