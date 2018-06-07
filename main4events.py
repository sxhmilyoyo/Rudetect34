import click
import os
import subprocess
import time
import random


@click.command()
@click.option('--rootpath', '-r', help='the root path of data')
def main(rootpath):
    """Run getTopicPmi and extractSubject atuomatically."""
    folders = [folder for folder in os.listdir(rootpath) if os.path.isdir(rootpath+"/"+folder)]
    print(folders)
    for folder in folders:
        if folder != 'Gabapentin_0628_0121':
            continue
        print ("Running code for {}".format(folder))
        args = ['python', 'main.py', '-r', '/home/hao/Workplace/HaoXu/Data/Rudetect_test',
                '-f', folder, '-q', 'test', '-s', 'test', '-e', 'test']
        subprocess.call(args)
        time.sleep(random.randint(1, 121))


if __name__ == '__main__':
    main()
