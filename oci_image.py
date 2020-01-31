from pathlib import Path

import yaml
from ops.framework import Object
from ops.model import BlockedStatus, ModelError


class OCIImageResource(Object):
    def __init__(self, charm, resource_name):
        super().__init__(charm, resource_name)
        self.resource_name = resource_name

    def fetch(self):
        resource_path = self.model.resources.fetch(self.resource_name)
        if not resource_path.exists():
            raise MissingResourceError(self.resource_name)
        resource_text = Path(resource_path).read_text()
        if not resource_text:
            raise MissingResourceError(self.resource_name)
        try:
            resource_data = yaml.safe_load(resource_text)
        except yaml.YAMLError as e:
            raise InvalidResourceError(self.resource_name)
        else:
            return ImageInfo(resource_data)


class ImageInfo(dict):
    def __init__(self, data):
        # Translate the data from the format used by the charm store to the format
        # used by the Juju K8s pod spec, since that is how this is typically used.
        super().__init__({
            'imagePath': data['registrypath'],
            'username': data['username'],
            'password': data['password'],
        })

    @property
    def image_path(self):
        return self['imagePath']

    @property
    def username(self):
        return self['username']

    @property
    def password(self):
        return self['password']


class MissingResourceError(ModelError):
    def __init__(self, resource_name):
        super().__init__(resource_name, BlockedStatus(f'Missing resource: {resource_name}'))


class InvalidResourceError(ModelError):
    def __init__(self, resource_name):
        super().__init__(resource_name, BlockedStatus(f'Invalid resource: {resource_name}'))
