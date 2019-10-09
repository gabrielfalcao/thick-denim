# -*- coding: utf-8 -*-
from mock import patch
from pathlib import PurePath

from thick_denim.config import ThickDenimConfig
from tests.harnesses import stub


def create_stub_of_thick_denim_config(data):
    return ThickDenimConfig(path="/path/to/dummy/config.yml", data=data)


@patch("thick_denim.config.load_yaml_data_from_path")
@patch("thick_denim.config.guess_config_path")
def test_thick_denim_config_tries_to_determine_the_config_path(
    guess_config_path, load_yaml_data_from_path
):
    "ThickDenimConfig() tries to find thick_denim yaml config from default conventional paths"

    # Given an empty config
    load_yaml_data_from_path.return_value = {}
    # And that that guess_config_path stubs its return value
    guess_config_path.return_value = "/some/dummy/path.yml"

    # When I instantiate ThickDenimConfig without passing a path argument
    conf = ThickDenimConfig()

    # Then it should have looked up in the conventional config path locations
    guess_config_path.assert_called_once()

    # And the config path should come from my stubbed value
    conf.path.should.equal("/some/dummy/path.yml")
