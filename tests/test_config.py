from brownie.test import given, strategy


@given(duration=strategy("uint256", min_value=1, max_value=1000))
def test_available(ygift, chain, duration):
    amount = 10 ** 18
    start = chain[-1].timestamp
    assert ygift.available(amount, start, duration) == 0
    chain.sleep(500)
    chain.mine()
    expected = amount * min(chain[-1].timestamp - start, duration) // duration
    assert ygift.available(amount, start, duration) == expected
    chain.sleep(1000)
    chain.mine()
    assert ygift.available(amount, start, duration) == amount


def test_available_instant(ygift, chain):
    amount = 10 ** 18
    start = chain[-1].timestamp
    assert ygift.available(amount, start, 0) == amount
