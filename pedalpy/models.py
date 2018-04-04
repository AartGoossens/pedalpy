import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.core.accessor import AccessorProperty
import pandas.plotting._core as gfx


def torque_column_labels():
    return [f'torque_{i}' for i in range(361)]


class RevolutionPlotMethods(gfx.FramePlotMethods):
    polar_angles = np.arange(0, 361) / (180 / np.pi)
    torque_columns = torque_column_labels()

    def polar(self, *args, **kwargs):
        ax = plt.subplot(111, projection='polar')

        torque = self._data[self.torque_columns].mean()

        ax.plot(self.polar_angles, torque, *args, **kwargs)

        ax.set_theta_offset(np.pi/2)
        # ax.set_theta_direction(-1)

        xticks_num = 8
        xticks = np.arange(0, 2*np.pi, 2 * np.pi / xticks_num)
        ax.set_xticks(xticks)
        rad_to_label = lambda i: '{}°'.format(int(i / (2 * np.pi) * 360) % 180)
        ax.set_xticklabels([rad_to_label(i) for i in xticks])
        ax.set_yticklabels([])

        return ax


class RevolutionDataFrame(pd.DataFrame):
    @property
    def _constructor(self):
        return RevolutionDataFrame

    def compute_min_max_angles(self):
        # @TODO this method is quite memory inefficient. Row by row calculation is better
        torque_columns = torque_column_labels()
        torque_T = self.loc[:, torque_columns].transpose().reset_index(drop=True)

        left_max_angle = torque_T.iloc[:180].idxmax()
        right_max_angle = torque_T.iloc[180:].idxmax() - 180
        
        left_min_angle = pd.concat([torque_T.iloc[:135], torque_T.iloc[315:]]).idxmin()
        right_min_angle = torque_T.iloc[135:315].idxmin() - 180

        left_max = pd.DataFrame(left_max_angle)
        right_max = pd.DataFrame(right_max_angle)
        left_min = pd.DataFrame(left_min_angle)
        right_min = pd.DataFrame(right_min_angle)

        return left_max, right_max, left_min, right_min

    def _average_by_column(self, column_name):
        averaged_self = self.groupby(column_name).mean().reset_index()
        return RevolutionDataFrame(averaged_self)


RevolutionDataFrame.plot = AccessorProperty(RevolutionPlotMethods,
        RevolutionPlotMethods)
