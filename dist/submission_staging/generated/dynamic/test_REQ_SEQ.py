def follows_sequence(history):
    expected = ['CREATED', 'PAID', 'SHIPPED', 'DELIVERED']
    position = 0
    for state in history:
        if position < len(expected) and state == expected[position]:
            position += 1
    return position == len(expected)


def test_REQ_SEQ_sequence():
    assert follows_sequence(['CREATED', 'PAID', 'SHIPPED', 'DELIVERED'])
    assert follows_sequence(['CREATED', 'PAID', 'SHIPPED', 'DELIVERED', 'DELIVERED'])
    assert not follows_sequence(['CREATED', 'DELIVERED'])
