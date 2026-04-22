import numpy as np
import xyz
from xyz.synthesis import QSPDatabase


def test_precompute_1():
    db = QSPDatabase()
    db.load_database(3)
