from datapanel_agent.compatibility import FIELDS, ROUTES, check


def document():
    result = {"paths": {p: {m: {} for m in methods} for p, methods in ROUTES.items()}}
    for path, fields in FIELDS.items():
        result["paths"][path]["post"]["requestBody"] = {
            "content": {
                "application/json": {
                    "schema": {"properties": {k: {} for k in fields}, "required": sorted(fields)}
                }
            }
        }
    return result


def test_current_routes_and_ignored_new_routes():
    value = document()
    value["paths"]["/v1/new-feature"] = {"get": {}}
    assert check(value)["compatible"]


def test_removed_route_and_new_required_field_are_detected():
    value = document()
    del value["paths"]["/v1/compute/usage"]
    schema = value["paths"]["/v1/compute/jobs"]["post"]["requestBody"]["content"][
        "application/json"
    ]["schema"]
    schema["properties"]["new_required"] = {}
    schema["required"].append("new_required")
    result = check(value)
    assert not result["compatible"]
    assert len(result["problems"]) == 2
