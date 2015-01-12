import sys
import re

def Error(msg):
    sys.exit(msg)

refExpr = re.compile("\{[0-9]+\}")
