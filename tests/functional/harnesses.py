# -*- coding: utf-8 -*-
import io
import json
import vcr
from pathlib import Path

functional_tests_path = Path(__file__).parent


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
    with io.open(filename, "w") as fp:
        json.dump(data, fp, indent=indent)
