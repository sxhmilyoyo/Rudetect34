#$ -N RuDetect34
#$ -m beas
#$ -M haoxu@udel.edu
# -l exclusive=1

vpkg_require anaconda/5.0.1:python3
source activate py36
python main.py