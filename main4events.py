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

    event2eps = {"BandyLee_0110_0115": 0.65,
                 "Capriccio_0516_0523_new": 0.5,
                 "Gabapentin_0628_0121": 0.35,
                 "immigrants_0622_0624": 0.3,
                 "Ingraham_0618_0624": 0.5,
                 "ItsJustAJacket_0621_0624": 0.45,
                 "JackBreuer_1228_0115": 0.6,
                 "JetLi_0519_0523": 0.6,
                 "SanctuaryCities_0516_0523": 0.3,
                 "SouthwestKey_0620_0624": 0.45,
                 "WhereAreTheChildren_0418_0527": 0.35}

    for folder in folders:
        # exclude some events
        if folder not in ["germanwings-crash-all-rnr-threads", "sydneysiege-all-rnr-threads"]:
            continue

        # specify an event
        # if folder != "immigrants_0622_0624":
        #     continue

        # run total events
        # if folder[0] == "." or folder in ["BandyLee_0110_0115", "Gabapentin_0628_0121", "Ingraham_0618_0624", "ItsJustAJacket_0621_0624", "SanctuaryCities_0516_0523", "WhereAreTheChildren_0418_0527"]:
        #     continue

        print("=" * 100)
        print("Running code for {}".format(folder))
        args = ['python', 'main.py', '-r', rootpath,
                '-f', folder, '-q', "#"+folder.split("_")[0],
                '-s', 'test', '-e', 'test', '-p',
                str(event2eps.get(folder, 'test'))]
        print("Command line is {}".format(" ".join(args)))
        with open("./output/"+folder+"_output.txt", "wb", 0) as out:
            subprocess.run(args, stdout=out, check=True)
        subprocess.call(args)
        # break
        time.sleep(random.randint(1, 121))


if __name__ == '__main__':
    main()
