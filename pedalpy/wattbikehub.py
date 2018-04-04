import collections
import datetime
import json
import re

import numpy as np
import pandas as pd
import requests

from .models import RevolutionDataFrame, torque_column_labels


WATTBIKE_HUB_LOGIN_URL = 'https://api.wattbike.com/v2/login'
WATTBIKE_HUB_RIDESESSION_URL = 'https://api.wattbike.com/v2/classes/RideSession'
WATTBIKE_HUB_FILES_BASE_URL = \
    'https://api.wattbike.com/v2/files/{user_id}_{session_id}.{extension}'
WATTBIKE_HUB_USER_URL = 'https://api.wattbike.com/v2/classes/_User'


def build_hub_files_url(user_id, session_id, extension='wbs'):
    return WATTBIKE_HUB_FILES_BASE_URL.format(
        user_id=user_id,
        session_id=session_id,
        extension=extension
    )


def flatten(d, parent_key='', sep='_'):
    """
    Credits for this method to: http://stackoverflow.com/users/1897/imran
    Posted on http://stackoverflow.com/a/6027615
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class WattbikeHubClient:
    def __init__(self, user_id=None):
        self.user_id = user_id

    def _create_request_session(self):
        headers = {'Content-Type': 'application/json'}
        session = requests.Session()
        session.headers = headers
        return session

    def get_activities_for_user(self, user_id=None, before=None, after=None):
        if user_id is None:
            if self.user_id is not None:
                user_id = self.user_id
            else:
                raise ValueError('user_id must be provided')

        if not before:
            before = datetime.datetime.now()
        if not after:
            after = datetime.datetime(2000, 1, 1)

        payload = {
            'where': {
                'user': {
                    '__type': 'Pointer',
                    'className': '_User',
                    'objectId': user_id},
                'startDate': {
                    '$gt': {
                        '__type': 'Date',
                        'iso': after.isoformat()},
                    '$lt': {
                        '__type': 'Date',
                        'iso': before.isoformat()
                    }
                }
            },
            '_method': 'GET',
            '_ApplicationId': 'Gopo4QrWEmTWefKMXjlT6GAN4JqafpvD',
            '_JavaScriptKey': 'p1$h@M10Tkzw#',
            '_ClientVersion': 'js1.6.14',
            '_InstallationId': 'f375bbaa-9514-556a-be57-393849c741eb'
        }

        with self._create_request_session() as session:
            resp = session.post(
                url=WATTBIKE_HUB_RIDESESSION_URL,
                data=json.dumps(payload))

        if not resp.ok:
            # Because Wattbike does not understand http status codes
            resp.reason = resp.content
        resp.raise_for_status()

        ride_sessions = resp.json()['results']

        activities = []
        for ride_session in ride_sessions:
            session_id = ride_session['objectId']
            activities.append(self.get_activity(session_id, user_id))

        return activities

    def get_activity(self, session_id, user_id=None):
        if user_id is None:
            if self.user_id is not None:
                user_id = self.user_id
            else:
                raise ValueError('user_id must be provided')

        if not re.match('\A[a-zA-Z0-9]{10}\Z', session_id):
            raise ValueError(
                'The provided session_id seems to belong to an earlier version '
                'of the Wattbike Hub API which is not supported'
            )
        response = requests.get(
            build_hub_files_url(user_id, session_id)
        )
        response.raise_for_status()
        raw_data = response.json()

        rdf = self._raw_data_to_rdf(raw_data, session_id, user_id)
        rdf = self._add_polar_forces(rdf)

        return rdf

    def _raw_data_to_rdf(self, session_data, session_id, user_id):
        rdf = RevolutionDataFrame(
            [flatten(rev) for lap in session_data['laps'] for rev in lap['data']])

        rdf['time'] = rdf.time.cumsum()
        rdf['user_id'] = user_id
        rdf['session_id'] = session_id

        for col in rdf.columns:
            try:
                rdf.iloc[:, rdf.columns.get_loc(col)] = \
                    pd.to_numeric(rdf.iloc[:, rdf.columns.get_loc(col)])
            except ValueError:
                continue

        return rdf

    def _add_polar_forces(self, rdf):
        _df = pd.DataFrame()
        new_angles = np.arange(0.0, 361.0)
        column_labels = torque_column_labels()

        if not '_0' in rdf.columns:
            for label in column_labels:
                rdf[label] = np.nan

        for index, pf in rdf.polar_force.iteritems():
            if not isinstance(pf, str):
                continue

            forces = [int(i) for i in pf.split(',')]
            forces = np.array(forces + [forces[0]])
            forces = forces/np.mean(forces)

            angle_dx = 360.0 / (len(forces)-1)

            forces_interp = np.interp(
                x=new_angles,
                xp=np.arange(0, 360.01, angle_dx),
                fp=forces)

            _df[index] = forces_interp

        _df['angle'] = column_labels
        _df.set_index('angle', inplace=True)
        _df = _df.transpose()

        for angle in column_labels:
            rdf[angle] = _df[angle]

        return rdf

    def get_user_id_from_session_url(self, session_url):
        session_data, ride_session = self.get_session(session_url)
        return ride_session['user']['objectId']

