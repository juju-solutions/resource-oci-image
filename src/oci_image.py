from pathlib import Path
from typing import Dict

import yaml
from ops.framework import Object
from ops.model import BlockedStatus, ModelError


class OCIImageResource(Object):
    def __init__(self, charm, resource_name):
        super().__init__(charm, resource_name)
        self.resource_name = resource_name

    def fetch(self) -> Dict:
        try:
            resource_path = self.model.resources.fetch(self.resource_name)
        except ModelError as e:
            raise MissingResourceError(self.resource_name) from e
        if not resource_path.exists():
            raise MissingResourceError(self.resource_name)
        resource_text = Path(resource_path).read_text()
        if not resource_text:
            raise MissingResourceError(self.resource_name)
        try:
            resource_data = yaml.safe_load(resource_text)
        except yaml.YAMLError as e:
            raise InvalidResourceError(self.resource_name) from e
        else:
            # Translate the data from the format used by the charm store to the
            # format used by the Juju K8s pod spec, since that is how this is
            # typically used.
            try:
                registry_path = resource_data['registrypath']
            except KeyError as e:
                raise InvalidResourceError(self.resource_name) from e
            return {
                'imagePath': registry_path,
                'username': resource_data.get('username', ''),
                'password': resource_data.get('password', ''),
            }


class OCIImageResourceError(ModelError):
    status_type = BlockedStatus
    status_message = 'Resource error'

    def __init__(self, resource_name):
        super().__init__(resource_name)
        self.status = self.status_type(
            '{}: {}'.format(self.status_message, resource_name))


class MissingResourceError(OCIImageResourceError):
    status_message = 'Missing resource'


class InvalidResourceError(OCIImageResourceError):
    status_message = 'Invalid resource'
