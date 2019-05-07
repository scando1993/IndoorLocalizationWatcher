import time


class Wifi:
    # It should have the following format ["aa:bb:cc", -80, "aa:bb:c0", -79]
    def __init__(self, wifis):
        self.wifis = wifis

    def gen_wifi_dict(self):
        dict = {}
        for i in range(0, len(self.wifis), 2):
            dict[self.wifis[i]] = int(self.wifis[i + 1])
        return dict


class WifiFingerprint:
    def __init__(self, family, device, location, wifis):
        self.f = family
        self.d = device
        self.t = int(time.time() * 1000)
        self.l = location
        self.s = {}
        wifi_obj = Wifi(wifis)
        self.s['wifi'] = wifi_obj.gen_wifi_dict()

    def __str__(self):
        return self.__dict__

    def __repr__(self):
        return self.__str__()