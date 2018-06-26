import click
import os
import subprocess
import time
import random


@click.command()
@click.option('--rootpath', '-r', help='the root path of data')
def main(rootpath):
    """Run getTopicPmi and extractSubject atuomatically."""
    folders = [folder for folder in os.listdir(
        rootpath) if os.path.isdir(rootpath+"/"+folder)]
    print("="*100)
    print(folders)
    print("="*100)

    for folder in folders:
        # if folder in ["immigration_0612_0624", "FalseFlag_0518_0523",  "Capriccio_0516_0523"]:
        #     continue
        if folder != "WhereAreTheChildren_0418_0527":
            continue
        print("Running code for {}".format(folder))
        args = ['python', 'main.py', '-r', rootpath,
                '-f', folder, '-q', "#"+folder.split("_")[0], '-s', 'test', '-e', 'test']
        print("Command line is {}".format(" ".join(args)))
        subprocess.call(args)
        time.sleep(random.randint(1, 121))


if __name__ == '__main__':
    main()
