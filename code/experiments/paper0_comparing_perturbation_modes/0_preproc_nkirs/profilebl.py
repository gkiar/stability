from bids.layout import BIDSLayout
import cProfile
import time

def myfunc(datadir):
    start = time.time()
    bl = BIDSLayout(datadir, exclude='sub-(?!A00010893)(.*)$')
    dur = time.time() - start
    print("{0}:{1}".format(len(bl.get_subjects()), dur))


ddir1 = '/project/6008063/gkiar/data/smallRS/'
ddir2 = '/project/6008063/gkiar/data/medRS/'
ddir3 = '/project/6008063/gkiar/data/RocklandSample/'

cProfile.run('myfunc(ddir3)')
# cProfile.run('myfunc(ddir2)')

# start3 = time.time()
# bl = BIDSLayout('/project/6008063/gkiar/data/RocklandSample/')
# dur3 = time.time() - start3
# print("{0}:{1}".format(len(bl.get_subjects()), dur3))
