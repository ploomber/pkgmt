from pkgmt.dependencies import Package


def test_package():
    a = Package("a")
    a.last_updated = "2022-12-21T09:48:51.773683Z"

    b = Package("b")
    b.last_updated = "2023-12-21T09:48:51.773683Z"

    assert a < b
    assert sorted([b, a]) == [a, b]
