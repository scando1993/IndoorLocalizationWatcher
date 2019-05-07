import numpy as np
import scipy.stats
import matplotlib.pyplot as plt


class WifiFingerprintStatistics:
    def __init__(self, rssi_array, absolute=False):
        if absolute:
            self.data = np.absolute(rssi_array)
        else:
            self.data = np.array(rssi_array)
        self.min = np.min(self.data)
        self.max = np.max(self.data)
        self.mean = np.mean(self.data)
        self.std = np.std(self.data)
        self.len_rssi = len(self.data)
        self.std_coeff = self.std / self.mean * 100
        self.resampled_data = []
        try:
            self.data_distribution = self.gen_distribution()
        except ValueError as e:
            self.data_distribution = None
            print(e)

    # Distribution generated from Beta function
    def gen_distribution(self):
        scale = self.max - self.min
        location = self.min

        # Mean and standard deviation of the unscaled Beta distribution
        unscaled_mean = (self.mean - self.min) / scale
        unscaled_var = (self.std / scale) ** 2

        # Computation of alpha and beta can be derived from mean and
        # variance formulas
        t = unscaled_mean / (1 - unscaled_mean)
        beta = ((t / unscaled_var) - (t * t) - (2 * t) - 1) / ((t * t * t) + (3 * t * t) + (3 * t) + 1)
        alpha = beta * t

        # Not all parameters produce a valid distribution
        if alpha <= 0 and beta <= 0:
            raise ValueError("Cannot create distribution for the given parameters.")

        # Make scaled beta distribution with computed parameters
        return scipy.stats.beta(alpha, beta, scale=scale, loc=location)

    def plot_distribution(self):
        if self.data_distribution is None:
            print("No distribution available")
            return

        x = np.linspace(self.min, self.max, self.mean, self.std)
        plt.plot(x, self.data_distribution.pdf(x))
        plt.show()

    def stats_distribution(self):
        print(" ")
        if len(self.resampled_data) > 0:
            print("Original min: %s, Generated min: %s"%(self.min, self.resampled_data.min()))
            print("Original max: %s, Generated max: %s"%(self.max, self.resampled_data.max()))
        if self.data_distribution is not None:
            print("Original mean: %s, Generated mean: %s"%(self.mean, self.data_distribution.mean()))
            print("Original std: %s, Generated std: %s" % (self.std, self.data_distribution.std()))
        print(" ")

    def rvs_distribution(self, n_samples):
        if self.data_distribution is not None:
            try:
                self.resampled_data = self.data_distribution.rvs(size=n_samples)
            except Exception as e:
                print(e)

    def __str__(self):
        return "{\n\t\tmean: %s\n\t\tstd: %s\n\t\tstd_coeff: %s\n\t}\n" % (self.mean, self.std, self.std_coeff)

    def __repr__(self):
        return self.__str__()