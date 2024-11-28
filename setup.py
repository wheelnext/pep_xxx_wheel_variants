"""
This is a protect setup.py file to prevent the parent project
from being built or uploaded.
"""
raise RuntimeError("The parent project should never be built nor uploaded.")