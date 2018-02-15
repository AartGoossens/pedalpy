from pedalpy import teamzwatt
from pedalpy.models import RevolutionDataFrame
from pedalpy.tools import label_revolutions, unstack_revolutions


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

    def test_rev_things(self):
        fname = 'tests/fixtures/teamzwatt1.txt'
        rdf = teamzwatt.import_from_file(fname)
        rdf = rdf.assign(revolution=label_revolutions(rdf.angle))
        rdf = unstack_revolutions(rdf)

        assert len(rdf) == 4165

        column_labels = rdf.columns.values
        assert 'torque_0' in column_labels
        assert 'y_force_0' in column_labels
        assert 'x_force_0' in column_labels
