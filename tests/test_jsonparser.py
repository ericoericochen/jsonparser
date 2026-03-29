import json

from jsonparser.parser import json_loads


def test_parse_string():
    json_string = json.dumps("hello world")
    assert json_loads(json_string) == json.loads(json_string)


def test_parse_number_int():
    json_string = json.dumps(12345)
    assert json_loads(json_string) == json.loads(json_string)


def test_parse_number_float():
    json_string = json.dumps(12345.12345)
    assert json_loads(json_string) == json.loads(json_string)


def test_parse_true_boolean():
    json_string = json.dumps(True)
    assert json_loads(json_string) == json.loads(json_string)


def test_parse_false_boolean():
    json_string = json.dumps(False)
    assert json_loads(json_string) == json.loads(json_string)


def test_parse_empty_dict():
    json_string = json.dumps({})
    assert json_loads(json_string) == json.loads(json_string)


def test_parse_simple_dict():
    json_string = json.dumps({"name": "John Doe", "age": 18, "can_drive": False})
    assert json_loads(json_string) == json.loads(json_string)


def test_nested_dict():
    json_string = json.dumps({"a": {"b": {"c": {"d": {"e": True}}}}})
    assert json_loads(json_string) == json.loads(json_string)


def test_parse_empty_list():
    json_string = json.dumps([])
    assert json_loads(json_string) == json.loads(json_string)


def test_parse_nested_list():
    json_string = json.dumps(["a", ["b", ["c", "d", ["e", ["f", "g", ["h"]]]]]])
    assert json_loads(json_string) == json.loads(json_string)
