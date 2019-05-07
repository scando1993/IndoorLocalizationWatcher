import os
import json
import time
import tempfile
from tqdm import tqdm
from WiFiFingerprint import WifiFingerprint
from WifiFingerprintSender import WifiFingerprintSender
import string
import random
import base58


class WifiFingerprintGenerator:
    def __init__(self, family, device_name, location, file_name=None, limit=500, sender=None):
        self.fingerprints = []
        self.file_name = file_name
        self.family = family
        self.device_name = device_name
        self.location = location
        self.limit = limit
        self.sender = sender
        # self.fd, self.path = tempfile.mkstemp()
        self.fd = self.random_string(7)

    def to_base58(self, file_name):
        return base58.b58encode(file_name.encode('utf-8')).decode('utf-8')

    def from_base58(self, file_name):
        return base58.b58decode(file_name.encode('utf-8')).decode('utf-8')

    def random_string(self, length=6):
        letters_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_digits) for i in range(length))

    def add_fingerprint(self, wifi_data):
        fingerprint = WifiFingerprint(self.family, self.device_name, self.location, wifi_data)
        if len(self.fingerprints) < self.limit:
            self.fingerprints.append(fingerprint)
        else:
            print("Fingerprints full generating temporary file")
            time.sleep(0.001)
            self._generate_file()

    def _generate_file(self):
        with open(self.fd, 'a+') as tmp:
            for fingerprint in tqdm(self.fingerprints):
                x = json.dumps(fingerprint.__dict__)
                tmp.write(x + '\n')
                # time.sleep(0.05)
        time.sleep(0.001)
        print("Dumping locally stored fingerprints")
        self.fingerprints = []
        #
        # finally:
        #         print("Sending data to server")
        #         self.send_data(file=fd)
        #         os.remove(path)

    def send_data(self, num_lines=None):
        if self.file_name is None:
            with open(self.fd, "r") as tmp:
                for line in tqdm(tmp):
                    data = json.loads(line)
                    if self.sender is not None:
                        self.sender.send_data(data)
                    else:
                        print("Asuming request: %s" % line)
        else:
            print("Sending file: %s" % self.from_base58(self.file_name.split(".")[0]))
            with open(self.file_name, "r") as tmp:
                for line in tqdm(tmp, total=num_lines):
                    data = json.loads(line.strip())
                    if self.sender is not None:
                        self.sender.send_data(data)
                    else:
                        print("Asuming request: %s" % line)

    def generate_file(self, file_name, ext='jsons'):
        self.file_name = self.to_base58(file_name) + '.' + ext
        self._generate_file()
        try:
            os.rename(self.fd, self.file_name)
        except FileExistsError as e:
            os.remove(self.file_name)
            os.rename(self.fd, self.file_name)
