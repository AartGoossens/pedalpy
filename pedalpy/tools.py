import numpy as np
import pandas as pd

from .models import RevolutionDataFrame


def label_revolutions(angle):
    angle_diffs = angle - angle.shift(1)
    revolutions = []
    i = 0

    for x in angle_diffs:
        if x < -100:
            i += 1
        revolutions.append(i)

    return pd.Series(revolutions)


def resample(angles, y):
    angles = np.insert(angles, 0, angles[-1] - 360)
    angles = np.append(angles, 360 + angles[1])

    y = np.insert(y, 0, y[-1])
    y = np.append(y, y[1])

    new_angles = np.arange(0.0, 361.0)

    return np.interp(x=new_angles, xp=angles, fp=y)


def column_labels(label):
    return [f'{label}_{i}' for i in range(361)]


def normalize_to_median(array):
    median = np.median(array)
    if median:
        return array / median
    else:
        # The case where array contains only zeroes
        return array

def process_revolutions(df, normalize=True):
    df = df.assign(revolution=label_revolutions(df.angle))

    data_types = set(df.columns.values) & {'torque', 'x_force', 'y_force'}
    transformed_data = {dtype: [] for dtype in data_types}
    index = []

    for rev_index, subset in df.groupby('revolution'):
        for dtype in data_types:
            resampled_data = resample(subset.angle.values, subset[dtype].values)

            if normalize:
                resampled_data = normalize_to_median(resampled_data)

            transformed_data[dtype].append(resampled_data)

        index.append(rev_index)

    data_dict = {}
    for dtype in data_types:
        data_dict.update(
            dict(zip(column_labels(dtype), map(list, zip(*transformed_data[dtype]))))
        )

    return RevolutionDataFrame(
        data=data_dict,
        index=index
    )
