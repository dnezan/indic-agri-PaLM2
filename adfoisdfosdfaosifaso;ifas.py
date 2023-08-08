import os

os.environ["DYM_API_KEY"] = "dEjH1ViH.yG6Y3DNNuN18fMVJodnyOLoNXK7L0SJ9"

from dymaxionlabs.models import Estimator

pools_detector = Estimator.create(name="Pools detector",
                                  type="object_detection",
                                  classes=["pool"])
                                  