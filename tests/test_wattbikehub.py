import datetime

import pytest

from pedalpy import wattbikehub
from pedalpy.models import RevolutionDataFrame

@pytest.fixture
def client():
    return wattbikehub.WattbikeHubClient(user_id='u-1756bbba7e2a350')

class TestWattbikeHubClient:

    def test_get_activity(self, client):
        rdf = client.get_activity('2yBuOvd92C')
        assert isinstance(rdf, RevolutionDataFrame)
        assert len(rdf) == 5480
        column_labels = rdf.columns.values
        assert 'torque_0' in column_labels

    def test_get_activities_for_user(self, client):
        activities = client.get_activities_for_user(
            before=datetime.date(2017, 2, 16),
            after=datetime.date(2017, 2, 14),
        )

        assert len(activities) == 1
        rdf = activities[0]
        assert isinstance(rdf, RevolutionDataFrame)
        assert len(rdf) == 5480
        column_labels = rdf.columns.values
        assert 'torque_0' in column_labels
