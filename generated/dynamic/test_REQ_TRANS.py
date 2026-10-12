def valid_transition(source, target):
    return source == 'IDLE' and target == 'RUNNING'


def test_REQ_TRANS_transition():
    assert valid_transition('IDLE', 'RUNNING')
    assert not valid_transition('RUNNING', 'IDLE')
