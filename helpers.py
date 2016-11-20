
import requests


from .config import *

def get_areas():
    resp_areas = requests.get(url=url_areas)
    areas = {}
    for area in resp_areas.json()[0]['areas']:
        areas[area['name']] = area['id']

    return areas


def get_specializations():
    resp_specs = requests.get(url=url_specs)
    specs = []
    for spec_row in resp_specs.json():
        spec = {'id': spec_row['id'], 'name': spec_row['name'], 'specializations': []}
        for subspec in spec_row['specializations']:
            spec['specializations'].append({subspec['name']: subspec['id']})
        specs.append(spec)
    specs = sorted(specs, key=lambda d: int(d['id']))

    return specs
