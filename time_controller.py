import sys
import argparse
import logging
import time
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

sys.path.append("C:\\Users\\KNL2022\\Documents\\Entangled souurce")
from utils.common import connect, adjust_bin_width
from utils.acquisitions import acquire_histograms,run_hist, save_histograms
from utils.plot import plot_histograms, filter_histogram_bins


logger = logging.getLogger(__name__)

#################################################################
#################   TO BE FILLED BY USER   ######################
#################################################################

# Default Time Controller IP address
DEFAULT_TC_ADDRESS = "169.254.104.112"

# Default acquisition duration in seconds
DEFAULT_ACQUISITION_DURATION = 0.5

# Default histogram bin count
DEFAULT_BIN_COUNT = 20

# Default histogram bin width (None = automatically set the lowest possible bin width)
DEFAULT_BIN_WIDTH = 100

# Default file path where histograms are saved in CSV format (None = do not save)
DEFAULT_HISTOGRAMS_FILEPATH = 'C:\\Users\\KNL2022\\Documents\\Entangled souurce\\scpi_idq900\\python_programok\\hist_adatok\\histogram_adatok.csv'

# Default list of histograms to acquire
DEFAULT_HISTOGRAMS = [1, 2, 3, 4]

# Default log file path where logging output is stored
DEFAULT_LOG_PATH = None
'------------------------------------------------------------'

def time_controller_csatlakozas():
    try:
        tc = connect(DEFAULT_TC_ADDRESS)
        bin_width = adjust_bin_width(tc, DEFAULT_BIN_WIDTH)
    except AssertionError as e:
        logger.error(e)
        sys.exit(1)

    except ConnectionError as e:
        logger.exception(e)
        sys.exit(1)
    return [tc, DEFAULT_ACQUISITION_DURATION, bin_width, DEFAULT_BIN_COUNT, DEFAULT_HISTOGRAMS]
