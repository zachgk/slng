import sys
import re

def Error(msg):
    sys.exit(msg)

def applySubs(expr, subs):
    for s in subs:
        subStr = '(^|[\(+*/-])' + s + '\.'
        r = re.compile(subStr)
        if subs[s]:
            rep = subs[s] + '.'
        else:
            rep = ''
        expr = r.sub(rep, expr)
    return expr

refExpr = re.compile("\{[0-9]+\}")
