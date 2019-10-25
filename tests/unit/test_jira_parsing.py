# -*- coding: utf-8 -*-
from thick_denim.base import extract_field_properties


# def test_parse_simple_subfield():
#     given_input = '{state=OPEN}'

#     result = extract_field_properties(given_input)

#     result.should.equal({
#         "state": "OPEN",
#     })


# def test_parse_2_subfields():
#     given_input = '{dataType=pullrequest, state=OPEN}'

#     result = extract_field_properties(given_input)

#     result.should.equal({
#             "dataType": "pullrequest",
#             "state": "OPEN",
#     })


# def test_parse_simple_subfields():
#     given_input = '{dataType=pullrequest, state=OPEN, stateCount=2}'

#     result = extract_field_properties(given_input)

#     result.should.equal({
#             "dataType": "pullrequest",
#             "state": "OPEN",
#             "stateCount": '2',
#     })


# def test_parse_simple_subfield_with_braces():
#     given_input = '{test={foo=bar}}'

#     result = extract_field_properties(given_input)

#     result.should.equal({
#         "test": {
#             "foo": "bar",
#         }
#     })


# def test_parse_simple_subfield_with_braces_with_subfield_with_braces():
#     given_input = '{test={foo={baz=chucknorris}}}'

#     result = extract_field_properties(given_input)

#     result.should.equal({
#         "test": {
#             "foo": {
#                 "baz": "chucknorris"
#             },
#         }
#     })


# def test_parse_simple_subfield_with_braces_and_siblings():
#     given_input = '{test={foo=bar, chuck=norris}}'

#     result = extract_field_properties(given_input)

#     result.should.equal({
#         "test": {
#             "foo": "bar",
#             "chuck": "norris",
#         }
#     })


# def test_parse_subfield():
#     given_input = '{pullrequest={dataType=pullrequest, state=OPEN, stateCount=2}'

#     result = extract_field_properties(given_input)

#     result.should.equal({
#         "pullrequest": {
#             "dataType": "pullrequest",
#             "state": "OPEN",
#             "stateCount": 2,
#         }
#     })
