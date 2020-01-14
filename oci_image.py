from pathlib import Path

import yaml
from ops.framework import Object
from ops.model import BlockedStatus


class OCIImageResource(Object):
    def __init__(self, parent, resource_name):
        super().__init__(parent, resource_name)
        self.resource_name = resource_name
        self.registry_path = None
        self.username = None
        self.password = None

    def fetch(self):
        resource_path = self.model.resources.fetch(self.resource_name)
        resource_text = Path(resource_path).read_text()
        if not resource_text:
            raise FetchError('empty yaml')
        try:
            resource_data = yaml.safe_load(resource_text)
        except yaml.YAMLError as e:
            raise FetchError(f'invalid yaml: {resource_text}') from e
        else:
            self.registry_path = resource_data['registrypath']
            self.username = resource_data['username']
            self.password = resource_data['password']


class FetchError(Exception):
    def __init__(self, name, reason):
        super().__init__(reason)
        self.name = name
        self.reason = reason
        self.status = BlockedStatus(f'Unable to fetch resource {name}: {reason}')
