import unittest
from pathlib import Path
from unittest import mock

from ops.model import ModelError

from oci_image import OCIImageResource


class TestOCIImageResource(unittest.TestCase):
    @mock.patch("ops.charm.CharmBase")
    def test_when_fetch_fails_with_model_error(self, charm):
        # Given
        resource = OCIImageResource(charm, "test-image")

        # Monkeypatch fetch as we can't mock the parent Object
        def patched_fetch(name: str) -> Path:
            raise ModelError()

        resource.model.resources.fetch = patched_fetch

        # When
        with self.assertRaises(Exception) as context:
            resource.fetch()

        # Then
        self.assertTrue("Missing resource: test-image", str(context.exception))

    @mock.patch("ops.charm.CharmBase")
    @mock.patch.object(Path, "exists")
    def test_when_resource_path_does_not_exist(self, path_exists, charm):
        # Given
        resource = OCIImageResource(charm, "test-image")

        # Monkeypatch fetch as we can't mock the parent Object
        def patched_fetch(name: str) -> Path:
            return Path("/a/b/c/d/e/f")

        resource.model.resources.fetch = patched_fetch
        path_exists.return_value = False

        # When
        with self.assertRaises(Exception) as context:
            resource.fetch()

        # Then
        self.assertTrue("Missing resource: test-image", str(context.exception))

    @mock.patch("ops.charm.CharmBase")
    @mock.patch.object(Path, "exists")
    @mock.patch.object(Path, "read_text")
    def test_when_resource_file_is_empty(self, read_text, path_exists, charm):
        # Given
        resource = OCIImageResource(charm, "test-image")

        # Monkeypatch fetch as we can't mock the parent Object
        def patched_fetch(name: str) -> Path:
            return Path("/a/b/c/d/e/f")

        resource.model.resources.fetch = patched_fetch
        path_exists.return_value = True
        read_text.return_value = ""

        # When
        with self.assertRaises(Exception) as context:
            resource.fetch()

        # Then
        self.assertTrue("Missing resource: test-image", str(context.exception))

    @mock.patch("ops.charm.CharmBase")
    @mock.patch.object(Path, "exists")
    @mock.patch.object(Path, "read_text")
    def test_when_resource_is_not_a_well_formatted_yaml(
        self, read_text, path_exists, charm
    ):
        # Given
        resource = OCIImageResource(charm, "test-image")

        # Monkeypatch fetch as we can't mock the parent Object
        def patched_fetch(name: str) -> Path:
            return Path("/a/b/c/d/e/f")

        resource.model.resources.fetch = patched_fetch
        path_exists.return_value = True

        read_text.return_value = """
            item
                <<: *item_attributes
        """

        # When
        with self.assertRaises(Exception) as context:
            resource.fetch()

        # Then
        self.assertTrue("Invalid resource: test-image", str(context.exception))

    @mock.patch("ops.charm.CharmBase")
    @mock.patch.object(Path, "exists")
    @mock.patch.object(Path, "read_text")
    def test_when_resource_misses_registry_path(self, read_text, path_exists, charm):
        # Given
        resource = OCIImageResource(charm, "test-image")

        # Monkeypatch fetch as we can't mock the parent Object
        def patched_fetch(name: str) -> Path:
            return Path("/a/b/c/d/e/f")

        resource.model.resources.fetch = patched_fetch
        path_exists.return_value = True

        read_text.return_value = """
            "username": {}
            "password": {}
        """

        # When
        with self.assertRaises(Exception) as context:
            resource.fetch()

        # Then
        self.assertTrue("Invalid resource: test-image", str(context.exception))

    @mock.patch("ops.charm.CharmBase")
    @mock.patch.object(Path, "exists")
    @mock.patch.object(Path, "read_text")
    def test_when_complete_image_info_should_match_given_resource(
        self, read_text, path_exists, charm
    ):
        # Given
        resource = OCIImageResource(charm, "test-image")

        # Monkeypatch fetch as we can't mock the parent Object
        def patched_fetch(name: str) -> Path:
            return Path("/a/b/c/d/e/f")

        resource.model.resources.fetch = patched_fetch
        path_exists.return_value = True

        image = "image:6.0"
        user = "user"
        pwd = "pwd"
        read_text.return_value = """
            "registrypath": {}
            "username": {}
            "password": {}
        """.format(
            image, user, pwd
        )

        # When
        image_info = resource.fetch()

        # Then
        self.assertDictEqual(
            image_info, {"imagePath": image, "password": pwd, "username": user}
        )

    @mock.patch("ops.charm.CharmBase")
    @mock.patch.object(Path, "exists")
    @mock.patch.object(Path, "read_text")
    def test_when_partial_image_info_should_match_given_resource(
        self, read_text, path_exists, charm
    ):
        # Given
        resource = OCIImageResource(charm, "test-image")

        # Monkeypatch fetch as we can't mock the parent Object
        def patched_fetch(name: str) -> Path:
            return Path("/a/b/c/d/e/f")

        resource.model.resources.fetch = patched_fetch
        path_exists.return_value = True

        image = "image:6.0"
        read_text.return_value = """
            "registrypath": {}
        """.format(
            image
        )

        # When
        image_info = resource.fetch()

        # Then
        self.assertDictEqual(image_info, {"imagePath": image})
