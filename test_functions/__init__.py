import pandas as pd
import numpy as np


def operate(n, d):
    return pd.concat([
        add(n, d), sub(n, d), mul(n, d), div(n, d)],
        axis=1
    )

def div(n, d):
    r = (n / d)
    return pd.DataFrame({"div": [r]})

def add(n, d):
    r = (n + d)
    return pd.DataFrame({"add": [r]})

def sub(n, d):
    r = (n - d)
    return pd.DataFrame({"sub": [r]})

def mul(n, d):
    r = (n * d) if n > 40 else n / d
    return pd.DataFrame({"mul": [r]})
