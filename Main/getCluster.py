# import click
import os
import sys
import time
sys.path.append('..')
# from Clustering.GetCluster import GetCluster
# from Utility.PreprocessData import PreprocessData
import Clustering
import Utility


# @click.command()
# @click.option('--rootpath', '-r', help='the root path of data')
# @click.option('--folderpath', '-f', help='the folder path of data')
# @click.option('--vectorizer', '-v', help='choose vectorizer(mean or tfidf)')
# @click.option('--numclusters', '-n', type=int, help='the number of cluster')
def main_cluster(rootpath, folderpath, vectorizer, numclusters):
    """Get main function for getCluster."""
    folderPath = os.path.join(folderpath, 'final')
    vectorizer = vectorizer
    numClusters = numclusters
    preprocessor = Utility.PreprocessData(rootpath)
    gc = Clustering.GetCluster(vectorizer, rootpath)
    # get the kmeans model
    print ("Getting the k-means model...")
    startTime = time.time()
    km = gc.getKmeans(folderPath, numClusters)
    print ("---------- K-means: {} seconds ----------".
           format(time.time() - startTime))
    # get the doc2Label
    print("Getting doc to label...")
    gc.getDoc2Label(folderPath, km)
    # get Label2Doc
    print("Getting label to doc...")
    gc.getLabel2Doc(folderPath, km)
    # get tweets.pkl for each clusters
    print("Storing tweets for clusters...")
    preprocessor.storeTweets4Clusters(folderPath)


if __name__ == '__main__':
    # startTime = time.time()
    main_cluster()
    # print ("---------- {} seconds ----------" % (time.time() - startTime))
