# -*- coding: utf-8 -*-

import json
import vcr
from pathlib import Path

functional_tests_path = Path(__file__).parent
tests_path = functional_tests_path.parent
data_output_path = tests_path.joinpath('data-output')


def vcr_for_domain(domain_name: str, record_mode="once"):
    return vcr.VCR(
        cassette_library_dir=str(
            functional_tests_path.joinpath(".vcr-cassetes", domain_name)
        ),
        # record_mode='new_episodes',
        record_mode=record_mode,
        match_on=["method", "scheme", "host", "port", "path", "query"],
    )


def dump_json(filename, data, indent=4):
    data_output_path.mkdir(exist_ok=True, parents=True)
    destination = data_output_path.joinpath(filename)
    with destination.open("w") as fp:
        json.dump(data, fp, indent=indent)
