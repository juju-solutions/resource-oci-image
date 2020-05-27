# OCI Image Resource helper

This is a helper for working with OCI image resources in the charm operator
framework.

## Installation

It will need to be vendored into your charm, using something like:

```
pip install --target ./env git+https://github.com/juju-solutions/resource-oci-image
```

## Usage

You can use this within your charm class like so:

```python
from ops.charm import CharmBase
from ops.main import main
from oci_image import OCIImageResource, OCIImageResourceError

class MyCharm(CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.image = OCIImageResource(self, 'resource-name')
        self.framework.observe(self.on.start, self.on_start)

    def on_start(self, event):
        try:
            image_info = self.image.fetch()
        except OCIImageResourceError as e:
            self.status = e.status
            event.defer()

if __name__ == "__main__":
    main(MyCharm)
```
