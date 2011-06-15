from jolly.map import LocationMask as FiringArc
from math import floor as f
from math import ceil as c

_tests = {
    'RF' : lambda x, y: x >= 0 and y + f(x / 2) <= 0,
    'LF' : lambda x, y: x <= 0 and y + f(-x / 2) <= 0,
    'R' : lambda x, y: x >= 0 and y + f(x / 2) >= 0 and y - c(x / 2) <= 0,
    'L' : lambda x, y: x <= 0 and y + f(-x / 2) >= 0 and y - c(-x / 2) <= 0,
    'RR' : lambda x, y: x >= 0 and y - c(x / 2) >= 0,
    'LR' : lambda x, y: x <= 0 and y - c(-x / 2) >= 0,
    'FH' : lambda x, y: y <= 0,
    'RH' : lambda x, y: x % 2 == 0 and y >= 0 or y > 0,
    'RP' : lambda x, y: (y + f(x / 2) * 3 + (0, 2)[x % 2]) <= 0,
    'LP' : lambda x, y: (y + f(-x / 2) * 3 + (0, 2)[x % 2]) <= 0,
    'RPR' : lambda x, y: (y + f(-x / 2) * 3 + (0, 2)[x % 2]) >= 0,
    'LPR' : lambda x, y: (y + f(x / 2) *  3 + (0, 2)[x % 2]) >= 0,
    'ALL' : lambda x, y: True }

del f
del c

RF = FiringArc('RF', (_tests['RF'],))
LF = FiringArc('LF', (_tests['LF'],))
R = FiringArc('R', (_tests['R'],))
L = FiringArc('L', (_tests['L'],))
RR = FiringArc('RR', (_tests['RR'],))
LR = FiringArc('LR', (_tests['LR'],))
FH = FiringArc('FH', (_tests['FH'],))
RH = FiringArc('RH', (_tests['RH'],))
RP = FiringArc('RP', (_tests['RP'],))
LP = FiringArc('LP', (_tests['LP'],))
RPR = FiringArc('RPR', (_tests['RPR'],))
LPR = FiringArc('LPR', (_tests['LPR'],))
FA = FiringArc('FA', (_tests['RF'], _tests['LF']))
RA = FiringArc('RA', (_tests['RR'], _tests['LR']))
ALL = FiringArc('ALL', (_tests['ALL'],))

del _tests

def setup_registry(registry):
    registry.set(RF.name, RF, FiringArc)
    registry.set(LF.name, LF, FiringArc)
    registry.set(R.name, R, FiringArc)
    registry.set(L.name, L, FiringArc)
    registry.set(RR.name, RR, FiringArc)
    registry.set(LR.name, LR, FiringArc)
    registry.set(FH.name, FH, FiringArc)
    registry.set(RH.name, RH, FiringArc)
    registry.set(RP.name, RP, FiringArc)
    registry.set(LP.name, LP, FiringArc)
    registry.set(RPR.name, RPR, FiringArc)
    registry.set(LPR.name, LPR, FiringArc)
    registry.set(FA.name, FA, FiringArc)
    registry.set(RA.name, RA, FiringArc)
    registry.set(ALL.name, ALL, FiringArc)
