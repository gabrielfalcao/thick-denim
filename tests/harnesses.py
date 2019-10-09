# -*- coding: utf-8 -*-
from thick_denim.config import ThickDenimConfig


def stub(base_class=None, **attributes):
    """creates a python class on-the-fly with the given keyword-arguments
    as class-attributes accessible with .attrname.

    The new class inherits from
    Use this to mock rather than stub.
    """
    if base_class is None:
        base_class = object

    members = {
        "__init__": lambda self: None,
        "__new__": lambda *args, **kw: object.__new__(
            *args, *kw
        ),  # remove __new__ and metaclass behavior from object
        "__metaclass__": type,
    }
    members.update(attributes)
    # let's create a python class on-the-fly :)
    return type(f"{base_class.__name__}Stub", (base_class,), members)()


def stub_config(data: dict):
    """returns a stub of ThickDenimConfig with fake data"""
    dummy_path = "/dummy/thick_denim-config.yml"
    return stub(ThickDenimConfig, path=dummy_path, __data__=data)


def stub_config_with_jira_account(
    account_name: str = "goodscloud",
    token: str = "sometoken",
    email: str = "gfalcao@newstore.com",
    **kwargs,
):
    """get a token in this URL

    """
    account_config = {
        "token": token,
        "email": email,
        "server": f"https://{account_name}.atlassian.net",
    }
    account_config.update(kwargs)

    return stub_config({"jira": {"accounts": {account_name: account_config}}})


def stub_config_with_github_token(
    token: str, **kwargs
):
    """to make real API requests create a token in this url https://github.com/settings/tokens
    """
    github_config = {"token": token}
    github_config.update(kwargs)

    return stub_config({"github": github_config})
