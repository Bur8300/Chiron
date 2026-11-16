from pathlib import Path

import pytest
import yaml
from fastapi.routing import APIRoute
from openapi_spec_validator import validate

from app.main import app

CONTRACT_PATH = Path(__file__).resolve().parents[2] / "contracts" / "openapi.yaml"
HTTP_METHODS = {"get", "post", "put", "patch", "delete"}
PUBLIC_OPERATIONS = {"getHealth", "activateAccount", "login", "refreshTokens"}
ROLES = {"student", "teacher", "administrator"}
ACCESS_CHECKS = {"self", "own", "assigned", "none"}


@pytest.fixture(scope="module")
def contract() -> dict:
    return yaml.safe_load(CONTRACT_PATH.read_text(encoding="utf-8"))


def operations(contract: dict):
    for path, item in contract["paths"].items():
        for method, operation in item.items():
            if method in HTTP_METHODS:
                yield path, method, operation


def test_contract_is_valid_openapi(contract: dict) -> None:
    validate(contract)


def test_operation_ids_are_unique(contract: dict) -> None:
    ids = [operation["operationId"] for _, _, operation in operations(contract)]
    assert len(ids) == len(set(ids))


def test_protected_operations_document_unauthorized(contract: dict) -> None:
    for path, method, operation in operations(contract):
        if operation.get("security") == []:
            continue
        assert "401" in operation["responses"], f"{method.upper()} {path}"


def test_only_allowed_operations_are_public(contract: dict) -> None:
    public = {
        operation["operationId"]
        for _, _, operation in operations(contract)
        if operation.get("security") == []
    }
    assert public == PUBLIC_OPERATIONS


def test_protected_operations_declare_roles_and_access(contract: dict) -> None:
    for path, method, operation in operations(contract):
        if operation["operationId"] in PUBLIC_OPERATIONS:
            continue
        name = f"{method.upper()} {path}"
        roles = operation.get("x-roles")
        assert roles, name
        assert set(roles) <= ROLES, name
        assert operation.get("x-access") in ACCESS_CHECKS, name
        if set(roles) != ROLES or operation["x-access"] != "self":
            assert "403" in operation["responses"], name


def test_error_responses_use_problem_json(contract: dict) -> None:
    shared = contract["components"]["responses"]
    for path, method, operation in operations(contract):
        for status, response in operation["responses"].items():
            if not status.startswith(("4", "5")):
                continue
            if "$ref" in response:
                response = shared[response["$ref"].rsplit("/", 1)[-1]]
            assert list(response["content"]) == ["application/problem+json"], (
                f"{method.upper()} {path} {status}"
            )


def test_api_paths_use_version_prefix(contract: dict) -> None:
    for path in contract["paths"]:
        assert path == "/health" or path.startswith("/api/v1/"), path


def test_every_backend_route_is_in_contract(contract: dict) -> None:
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        assert route.path in contract["paths"], route.path
        for method in route.methods:
            assert method.lower() in contract["paths"][route.path], f"{method} {route.path}"
