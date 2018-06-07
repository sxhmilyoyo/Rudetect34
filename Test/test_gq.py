import sys
sys.path.append("..")
import Information

def main():
    qg = Information.QueryGenerator("/local/data/haoxu/Rudetect", "Gabapentin_0628_0121/final/clusterData/0")
    qg.generateQ()

main()
