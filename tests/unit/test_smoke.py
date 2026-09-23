import honeypass


def test_package_version_is_exposed() -> None:
    assert honeypass.__version__ == "0.1.0"
