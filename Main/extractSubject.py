import sys
sys.path.insert(0, '..')
# import click
import codecs
import os
# from SVO.SubjectExtraction import SubjectExtraction
import SVO
# from Utility.Helper import Helper
import Utility


# @click.command()
# @click.option('--rootpath', '-r', help='the root path of data')
# @click.option('--folderpath', '-f', help='the folder path of data')
def main_extractsubject(rootpath, folderpath):
    """Extract the subjectsect."""
    # dataPath = "/local/data/haoxu/Rudetect/DevinKelley_Antifa/"
    folderPath = os.path.join(folderpath, 'final')
    fullPath = os.path.join(rootpath, folderPath)
    helper = Utility.Helper(rootpath)
    subjectExtraction = SVO.SubjectExtraction()
    with codecs.open(
            os.path.join(rootpath, folderPath, "tweets_line.txt"), "r",
            "utf-8") as fp:
        document = fp.read()
    print("Extracting subjects...")
    if not os.path.exists(os.path.join(rootpath, folderPath, 'subjects.json')):
        subjects = subjectExtraction.extract_subject(document)
        helper.dumpJson(folderPath, 'subjects.json', subjects)
        print("subjects.json has been saved.")
    else:
        subjects = helper.loadJson(os.path.join(folderPath, 'subjects.json'))
        print("subjects.json has been loaded.")
    subject2svos = {}
    for subject in subjects:
        print("extracting for subject: {}".format(subject))
        taggedSents = subjectExtraction.tag_sentences(fullPath, subject,
                                                      document)
        svos = [
            subjectExtraction.get_svo(sentence, subject)
            for sentence in taggedSents
        ]
        subject2svos[subject] = svos
    helper.dumpJson(folderPath, 'subject2svos.json', subject2svos)
    print("subject2svos.json has been saved.")


if __name__ == '__main__':
    main_extractsubject()
