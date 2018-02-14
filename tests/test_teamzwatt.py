from pedalpy import teamzwatt
from pedalpy.models import RevolutionDataFrame


class TestTeamZwatt:
    def test_import_from_file(self):
        fname = 'tests/fixtures/teamzwatt1.txt'
        rdf = teamzwatt.import_from_file(fname)

        assert isinstance(rdf, RevolutionDataFrame)
        assert len(rdf) == 211984

        column_labels = rdf.columns.values
        assert 'time' in column_labels
        assert 'x_force' in column_labels
        assert 'y_force' in column_labels
        assert 'power' in column_labels
        assert 'torque' in column_labels
        assert 'angle' in column_labels
        assert 'longitude' in column_labels
        assert 'latitude' in column_labels
