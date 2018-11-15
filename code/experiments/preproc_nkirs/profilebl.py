from bids.layout import BIDSLayout
import time

start1 = time.time()
bl = BIDSLayout('/project/6008063/gkiar/data/smallRS')
dur1 = time.time() - start1
print("{0}:{1}".format(len(bl.get_subjects()), dur1))


start2 = time.time()
bl = BIDSLayout('/project/6008063/gkiar/data/medRS/')
dur2 = time.time() - start2
print("{0}:{1}".format(len(bl.get_subjects()), dur2))

start3 = time.time()
bl = BIDSLayout('/project/6008063/gkiar/data/RocklandSample/')
dur3 = time.time() - start3
print("{0}:{1}".format(len(bl.get_subjects()), dur3))
