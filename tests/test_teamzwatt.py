import pandas as pd

from pedalpy import teamzwatt
from pedalpy.models import RevolutionDataFrame
from pedalpy import tools


class TestTeamZwatt:
    def test_load_raw_version_1(self):
        fname = 'tests/fixtures/teamzwatt1.txt'
        df = teamzwatt.load_raw(fname)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 324648

        column_labels = df.columns.values
        assert 'time' in column_labels
        assert 'x_force' in column_labels
        assert 'y_force' in column_labels
        assert 'power' in column_labels
        assert 'torque' in column_labels
        assert 'angle' in column_labels
        assert 'longitude' in column_labels
        assert 'latitude' in column_labels

    def test_load(self):
        fname = 'tests/fixtures/teamzwatt1.txt'
        df = teamzwatt.load_raw(fname)
        rdf = tools.process_revolutions(df)

        assert len(rdf) == 6370

        column_labels = rdf.columns.values
        assert 'torque_0' in column_labels
        assert 'y_force_0' in column_labels
        assert 'x_force_0' in column_labels
