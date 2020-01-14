from pathlib import Path

import yaml
from ops.framework import EventBase, EventSource, EventsBase, Object
from ops.model import BlockedStatus


class OCIImageAvailableEvent(EventBase):
    def __init__(self, handle, resource_data):
        super().__init__(handle)
        self.registry_path = resource_data['registrypath']
        self.username = resource_data['username']
        self.password = resource_data['password']

    def snapshot(self):
        return {
            'registry_path': self.registry_path,
            'username': self.username,
            'password': self.password,
        }

    def restore(self, snapshot):
        self.registry_path = snapshot['registry_path']
        self.username = snapshot['username']
        self.password = snapshot['password']


class OCIImageFailedEvent(EventBase):
    def __init__(self, handle, status_message):
        super().__init__(handle)
        self.status = BlockedStatus(status_message)

    def snapshot(self):
        return {
            'message': self.status.message,
        }

    def restore(self, snapshot):
        self.status = BlockedStatus(snapshot['message'])


class OCIImageEvents(EventsBase):
    image_available = EventSource(OCIImageAvailableEvent)
    image_failed = EventSource(OCIImageFailedEvent)


class OCIImageResource(Object):
    on = OCIImageEvents()

    def __init__(self, charm, resource_name):
        super().__init__(charm, resource_name)
        self.resource_name = resource_name

        self.framework.observe(charm.on.start, self.check_resource)
        self.framework.observe(charm.on.upgrade_charm, self.check_resource)

    def check_resource(self, event):
        resource_path = self.model.resources.fetch(self.resource_name)
        if not resource_path.exists():
            # TODO: log
            # self.model.log(f'Missing file for resource: {self.resource_name}')
            self.on.image_failed.emit(f'Missing resource: {self.resource_name}')
            return
        resource_text = Path(resource_path).read_text()
        if not resource_text:
            # TODO: log
            # self.model.log(f'Empty yaml for resource: {self.resource_name}')
            self.on.image_failed.emit(f'Missing resource: {self.resource_name}')
            return
        try:
            resource_data = yaml.safe_load(resource_text)
        except yaml.YAMLError as e:
            # TODO: log
            # self.model.log(f'Invalid resource yaml {self.resource_name}: {resource_text}')
            self.on.image_failed.emit(f'Invalid resource: {self.resource_name}')
        else:
            self.on.image_available.emit(resource_data)
