def ordering_holds(before, after):
    return not after or before


def test_REQ_ORDER_ordering():
    assert ordering_holds(False, False)
    assert ordering_holds(True, False)
    assert ordering_holds(True, True)
    assert not ordering_holds(False, True)
