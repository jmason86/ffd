import numpy as np
from matplotlib import pyplot as plt

class Flares(object):
    """
    A Flares object contains the energy (or other defining metric) of flares from a compendium of datasets
    (specifically FlareDataset objects).

    Attributes
    ----------
    datasets : list
        The FlareDataset objects making up Flares.
    n_total : int
        Total number of flares summed across all datasets.
    expt_total : float
        Total exposure time summed across all datasets.
    e : array
        Flare energies (or other defining metric) concatenated from all datasets and sorted in value.
    expt_detectable : array
        The total exposure time in which the event stored in "e" could have been detected. (I.e. the sum of the
        exposure times of datasets where the detection limit was below e.)
    cumfreq_naive : array
        Cumulative frequency of for events >=e assuming expt_total for all.
    cumfreq_corrected : array
        Cumulative frequency for events >=e accounting for differences in total time in which such events could have
        been detected.
    """

    def __init__(self, datasets):
        """
        Creat a Flares object.

        Parameters
        ----------
        datasets : list
            A list of FlareDataset objects. Make sure they use a consistent metric to characterize the flares (
            energy, equivalent duration, peak flux, etc.)

        Returns
        -------
        A Flares object :)

        """
        self.datasets = datasets

        # totals
        self.n_total = sum([data.n for data in datasets])
        self.expt_total = np.sum([data.expt for data in datasets])

        # event energies concatenated from all flare datasets
        self.e = np.concatenate([data.e for data in datasets])
        self.e = np.sort(self.e)

        # exposure time in which an event of energy e *could* have been detected
        expts = np.array([data.expt for data in datasets])
        elims = np.array([data.elim for data in datasets])
        isort = np.argsort(elims)
        elims, expts = [a[isort] for a in [elims, expts]]
        cumexpts = np.cumsum(expts)
        i_lims = np.searchsorted(elims, self.e, side='right')
        self.expt_detectable = cumexpts[i_lims-1]

        # cumulative frequencies ignoring differences in detection limits and correcting for them
        cumno = np.arange(self.n_total)[::-1] + 1
        self.cumfreq_naive = (cumno / self.expt_total)
        cumno_corrected = np.cumsum(1. / self.expt_detectable[::-1])[::-1] * self.expt_total
        self.cumfreq_corrected = cumno_corrected / self.expt_total

    def plot_ffd(self, *args, **kwargs):
        """
        Plot a step function of the flare frequency distribution, with the option to adjust for differences in
        detection limits.

        Parameters
        ----------
        args :
            passed to the matplotlib plot function
        ax :
            matplotlib axes object on which to draw line
        corrected : boolean
            Whether to use the naive or corrected cumulative frequency. The naive value is more common for large
            datasets and produces a drop-off of the expected power-law at low flare energies.
        kwargs :
            passed to the matplotlib plot function

        Returns
        -------
        line :
            matplotlib line object
        """
        ax = kwargs.get('ax', plt.gca())
        corrected = kwargs.get('corrected', True)
        cf = self.cumfreq_corrected if corrected else self.cumfreq_naive
        line, = ax.step(self.e, cf, where='post', **kwargs)
        return line


class FlareDataset(object):

    def __init__(self, detection_limit, exposure_time, flare_energies=[]):
        """
        Create a FlareDataset object.

        Parameters
        ----------
        detection_limit : float
            Minimum energy (or other flare metric) of a detectable event.
        exposure_time : float
            Total time in which flares could have been detected.
        flare_energies : array-like
            Energies (or other metric like equivalent duration, peak flux, ...) of the detected events. Use an empty
            list (default) if no events were detected but the dataset is still being included.
        """
        self.elim = detection_limit
        self.expt = exposure_time
        self.e = np.array(flare_energies)
        self.n = len(flare_energies)







