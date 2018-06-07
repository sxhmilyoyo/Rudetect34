import sys
sys.path.append("..")
# from Utility.GetHashtagPopularity import GetHashtagPopularity
import Utility


def getHashtagPopularity_main():
    ghp = Utility.GetHashtagPopularity('#Trump AND twitter', '/local/data/haoxu/Rudetect', 'BandyLee_0110_0115')
    ghp.start_crawl()

if __name__ == '__main__':
    getHashtagPopularity_main()
