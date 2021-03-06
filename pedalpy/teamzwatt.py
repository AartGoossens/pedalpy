import numpy as np
import pandas as pd

from .models import RevolutionDataFrame
from .tools import process_revolutions


DEFAULT_CALIBRATION_VALUE = -263
CRANK_LENGTH = 0.1725


def load_raw(filepath_or_buffer):
    return pd.read_csv(
        filepath_or_buffer=filepath_or_buffer,
        sep='\t',
        skiprows=range(13),
        index_col=0,
        names=['index', 'time', 'x_force', 'y_force', 'power', 'torque', 'cadence', 'angle', 'longitude', 'latitude']
    )


def load(filepath_or_buffer, normalize=True):
    raw_data = load_raw(filepath_or_buffer)
    return process_revolutions(raw_data, normalize)

def zero_offset(power, calibration_value=DEFAULT_CALIBRATION_VALUE):
    power = power + calibration_value
    return power.apply(lambda x: max(0, x))

def cadence_to_radians(cadence):
    return cadence / 60 * np.pi


def power_from_torque(torque, x_force, cadence_radians, calibration_value=DEFAULT_CALIBRATION_VALUE):
    power_from_torque = torque * cadence_radians
    power_from_x_force = x_force * 9.81 / 1000 * cadence_radians * CRANK_LENGTH
    return power_from_torque + power_from_x_force

def average_power_from_torque(power_from_torque, cadence):
    average_power = []
    cadence_for_current_group = cadence[0]
    power_for_current_group = []
    for pwr, cad in zip(power_from_torque, cadence):
        if cad != cadence_for_current_group:
            average_power = average_power + \
                [np.average(power_for_current_group)] * len(power_for_current_group)
            cadence_for_current_group = cad
            power_for_current_group = [cad]
        else:
            power_for_current_group.append(pwr)

    return pd.Series(average_power)


def postprocess_df(df):
    df = df.assign(power=zero_offset(df.power))
    df = df.assign(cadence_radians=cadence_to_radians(df.cadence))
    df = df.assign(revolution=group_revolutions(df.angle))
    df = df.assign(power_recalculated=power_from_torque(
        df.torque,
        df.x_force,
        df.cadence_radians
    ))
    df = df.assign(power_recalculated_averaged=average_power_from_torque(
        df.torque, df.cadence_radians
    ))
    return df
