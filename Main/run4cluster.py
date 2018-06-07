import click
import os
import subprocess


@click.command()
@click.option('--rootpath', '-r', help='the root path of data')
@click.option('--folderpath', '-f', help='the folder path of data')
def main(rootpath, folderpath):
    """Run getTopicPmi and extractSubject atuomatically."""
    folderPath = os.path.join(folderpath, 'final/clusterData')
    filenames = os.listdir(folderPath)
    for filename in filenames:
        fullPath = os.path.join(rootpath, folderPath, filename)
        print ("Running code for {}".format(fullPath))
        args = ['python', 'getTopicPmi.py', '-r', '/local/data/haoxu/Rudetect',
                '-f', fullPath, '-n', 1]
        print ("Running getTopicPmi.py ...")
        subprocess.call(args)
        args[1] = 'extractSubject.py'
        # args = ['python', 'extractSubject.py', '-r',
        #         '/local/data/haoxu/Rudetect', '-f', fullPath]
        print ("Running extractSubject.py ...")
        subprocess.call(args)


if __name__ == '__main__':
    main()
