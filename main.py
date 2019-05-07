from scipy.stats import gaussian_kde

from WifiFingerprintGenerator import WifiFingerprintGenerator
from WifiFingerprintSender import WifiFingerprintSender
from transpose_csv import data
from transpose_csv import transpose_data
import numpy as np
from scipy import stats
from WiFiFingerprintStatistics import WifiFingerprintStatistics
from WifiZoneAnalysis import WifiZoneAnalysis
import argparse
from matplotlib import pyplot

data_ = {}

description = '''
This is a program that permits analyze the Wifi fingerprint
-------------------------------------------------------------\n
Valid csv:\tLocations , Wifi-A , Wifi-B , Wifi-C\n
        \t\tLocation-A,   -92  ,        ,   -80\n
        \t\tLocation-B,   -82  ,  -20   ,   -10 \n
-------------------------------------------------------------
All should be with a delimiter and a sentence break character   
'''

if __name__ is '__main__':
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser(prog="Wifi Fingerprint Data Analyzer",
                                 description=description)
    ap.add_argument("-i", "--input", required=True,
                    help="Initial CSV with data fingerprints")
    ap.add_argument("-t", "--tolerance",
                    required=False,
                    default=3,
                    help="Set the tolerance value for the minimum amount of RSSI values per MAC")
    ap.add_argument("--config-file",
                    required=False,
                    help="All parameters can be passed as a config.json or yml")
    ap.add_argument("-T", "--tail", required=False,
                    help="Compute only the N last locations")
    ap.add_argument("-H", "--head", required=False,
                    help="Compute only the N first locations")
    ap.add_argument("-N", "--number-of-rows", required=False,
                    help="Compute only the N locations")
    ap.add_argument("--out-transpose",
                    required=False,
                    action='store_true',
                    default=False,
                    help="If initial data should be transpose")
    ap.add_argument("-o", "--out-json",
                    required=False,
                    default=False,
                    action='store_true',
                    help="If the final object should be saved as JSON")
    ap.add_argument("-s", "--statistics",
                    required=False,
                    default=False,
                    action='store_true',
                    help="Generate statistic data from each RSSI fingerprint")
    ap.add_argument("-c", "--count",
                    required=False,
                    default=False,
                    action='store_true',
                    help="Count the number of RSSI values for each MAC")
    ap.add_argument("-p", "--plot",
                    default=False,
                    action='store_true',
                    help="Generate a plot for each location using the RSSI values")
    ap.add_argument("-v", "--verbose",
                    required=False,
                    default=False,
                    action='store_true',
                    help="Add the level of verbose ")
    ap.add_argument("-a", "--all",
                    required=False,
                    default=False,
                    action='store_true',
                    help="Compute all the input file")
    ap.add_argument('--version', action='version', version='%(prog)s 0.1')
    args = vars(ap.parse_args())

    for location in transpose_data[0]:
        data_[location] = {}
        for wifi in data[0][1:]:
            data_[location][wifi] = []

    x = len(transpose_data)
    y = len(transpose_data[0])

    for i in range(1, x):
        for j in range(1, y):
            location = transpose_data[0][j]
            wifi = transpose_data[i][0]
            if transpose_data[i][j] is not '':
                data_[location][wifi].append(float(transpose_data[i][j]))

    data_.pop("location", None)

    aggregate_data = {}

    num_fing_data = {}

    for key in data_:
        num_fing_data[key] = 0

    for location in transpose_data[0][1:]:
        num_fing_data[location] += 1

    augment_data = 100

    wifi_data = {}
    for key in data_:
        wifi_data[key] = WifiZoneAnalysis()
        wifi_data[key].wifi_analysis["aggregate"] = {}
        wifi_data[key].wifi_analysis["stats"] = {}
        wifi_data[key].wifi_analysis["best_macs"] = []
        wifi_data[key].wifi_analysis["best_signals"] = {}
        for inner_key in data_[key]:
            wifi_arr = data_[key][inner_key]
            if len(data_[key][inner_key]) >= 4:
                wifi_data[key].wifi_analysis["aggregate"][inner_key] = wifi_arr
                wfpStats = WifiFingerprintStatistics(wifi_arr, absolute=False)
                # wfpStats.rvs_distribution(10000)
                # wfpStats.stats_distribution()
                # wifi_data[key].wifi_analysis["stats"][inner_key] = wfpStats
                # if wfpStats.mean < -60:
                if not np.less(wfpStats.mean, -60):
                    # wfpStats = WifiFingerprintStatistics(wifi_arr, absolute=False)
                    wfpStats.rvs_distribution(augment_data)
                    wfpStats.stats_distribution()
                    wifi_data[key].wifi_analysis["stats"][inner_key] = wfpStats
                    wifi_data[key].wifi_analysis["best_signals"][inner_key] = wifi_arr
                    wifi_data[key].wifi_analysis["best_macs"].append(inner_key)
                    wifi_data[key].wifi_thres_num += 1
                else:
                    wifi_data[key].wifi_num += 1

            elif len(wifi_arr) is not 0:
                wifi_data[key].noise_wifi[inner_key] = wifi_arr
                wifi_data[key].noise_num += 1

        wifi_data[key].total_num = wifi_data[key].noise_num + wifi_data[key].wifi_num + wifi_data[key].wifi_thres_num

    if args['plot']:
        bins = np.linspace(-100, 0, 100)
        for key in wifi_data:
            fig = pyplot.figure(figsize=(10, 4))
            for inner_key in wifi_data[key].wifi_analysis["best_signals"]:

                try:
                    density = gaussian_kde(wifi_data[key].wifi_analysis["best_signals"][inner_key])
                    density.covariance_factor = lambda: .5
                    density._compute_covariance()
                except Exception as e:
                    print(e)
                    continue
                pyplot.fill(bins, density(bins), alpha=0.2,  label=inner_key)

            pyplot.title(key)
            pyplot.legend(loc="upper right")
            pyplot.show()
            pyplot.close(fig)

    family = "test1"
    device = "ai"
    web_args = {'justsave': 0}
    wifiSender = WifiFingerprintSender("http://172.16.10.98:8005", "data", args=web_args)
    for key in wifi_data:
        location = key
        wfg = WifiFingerprintGenerator('semgroup_medialab', device, location, sender=wifiSender)
        for i in range(0, augment_data):
            wifis = []
            for inner_key in wifi_data[key].wifi_analysis["stats"]:
                augmented_data = wifi_data[key].wifi_analysis["stats"][inner_key].resampled_data
                if len(augmented_data) > 0:
                    wifi_name = inner_key[5:]
                    rssi = int(augmented_data[i])
                    wifis.append(wifi_name)
                    wifis.append(rssi)
            wfg.add_fingerprint(wifis)
        wfg.generate_file(location, ext='jsons')
        wfg.send_data(num_lines=augment_data)

    print(wifi_data)