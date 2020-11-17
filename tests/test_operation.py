import brownie
import pytest
from brownie import Wei


def test_mint(ygift, token, giftee, chain):
    amount = Wei("1000 ether")
    start = chain[-1].timestamp + 1000
    duration = 1000
    token.approve(ygift, 2 ** 256 - 1)
    ygift.mint(giftee, token, amount, "name", "msg", "url", start, duration)
    gift = ygift.gifts(0).dict()
    assert gift == {
        "token": token,
        "name": "name",
        "message": "msg",
        "url": "url",
        "amount": amount,
        "tipped": 0,
        "start": start,
        "duration": duration,
    }


def test_tip(ygift, token, giftee, chain):
    amount = Wei("1000 ether")
    tip = amount * 2
    start = chain[-1].timestamp
    token.approve(ygift, 2 ** 256 - 1)
    ygift.mint(giftee, token, amount, "name", "msg", "url", start, 1000)
    ygift.tip(0, tip, "tip")
    gift = ygift.gifts(0).dict()
    assert gift["amount"] == amount
    assert gift["tipped"] == tip
    # tips are available instantly
    chain.sleep(500)
    chain.mine()
    assert ygift.collectible(0) >= tip
    ygift.collect(0, tip, {"from": giftee})
    assert token.balanceOf(giftee) == tip


def test_tip_nonexistent(ygift, token):
    with brownie.reverts("yGift: Token ID does not exist."):
        ygift.tip(1, 1000, "nope")


def test_collect(ygift, token, giftee, chain):
    amount = Wei("1000 ether")
    start = chain[-1].timestamp + 1000
    duration = 1000
    token.approve(ygift, 2 ** 256 - 1)
    ygift.mint(giftee, token, amount, "name", "msg", "url", start, duration)

    with brownie.reverts("yGift: Rewards still vesting"):
        ygift.collect(0, amount, {"from": giftee})

    # excess requested amount is rounded down to available
    chain.sleep(1200)
    chain.mine()
    ygift.collect(0, amount, {"from": giftee})
    assert 0 < token.balanceOf(giftee) < amount

    chain.sleep(duration)
    chain.mine()

    with brownie.reverts("yGift: You are not the NFT owner"):
        ygift.collect(0, amount)

    ygift.collect(0, amount, {"from": giftee})
    assert token.balanceOf(giftee) == amount


@pytest.mark.parametrize("duration", [0, 10])
def test_collect_over_duration(ygift, token, giftee, chain, duration):
    amount = Wei("1000 ether")
    start = chain[-1].timestamp
    token.approve(ygift, 2 ** 256 - 1)
    ygift.mint(giftee, token, amount, "name", "msg", "url", start, 10)
    chain.sleep(duration)
    ygift.collect(0, amount * duration / 10, {"from": giftee})
    gift = ygift.gifts(0).dict()
    assert token.balanceOf(giftee) == amount * duration / 10
    assert gift["amount"] == amount - amount * duration / 10


@pytest.mark.parametrize("duration", [0, 10])
def test_tip_after_withdrawn(ygift, token, giftee, chain, duration):
    amount = Wei("1000 ether")
    tip = amount / 2
    start = chain[-1].timestamp
    token.approve(ygift, 2 ** 256 - 1)
    ygift.mint(giftee, token, amount, "name", "msg", "url", start, duration)
    chain.sleep(duration)
    ygift.collect(0, 2 ** 256 - 1, {"from": giftee})
    ygift.tip(0, tip, "tip")
    ygift.collect(0, 2 ** 256 - 1, {"from": giftee})
    gift = ygift.gifts(0).dict()
    assert gift["amount"] == 0
    assert gift["tipped"] == 0
    assert token.balanceOf(giftee) == amount + tip


def test_withdraw_before_and_after_transfer(ygift, token, giftee, receiver, chain):
    amount = Wei("100 ether")
    start = chain[-1].timestamp
    token.approve(ygift, 2 ** 256 - 1)
    ygift.mint(giftee, token, amount, "name", "msg", "url", start, 0)
    ygift.collect(0, amount / 2, {"from": giftee})
    gift = ygift.gifts(0).dict()
    assert gift["amount"] == amount / 2
    assert token.balanceOf(giftee) == amount / 2
    ygift.safeTransferFrom(giftee, receiver, 0, {"from": giftee})
    ygift.collect(0, amount / 4, {"from": receiver})
    gift = ygift.gifts(0).dict()
    assert gift["amount"] == amount / 4
    assert token.balanceOf(receiver) == amount / 4


def test_cannot_withdraw_more_than_gift_amount(ygift, token, giftee, chain):
    amount = Wei("100 ether")
    start = chain[-1].timestamp
    token.approve(ygift, 2 ** 256 - 1)
    ygift.mint(giftee, token, amount * 10, "name", "msg", "url", start, 0)

    ygift.collect(0, amount * 1, {"from": giftee})
    ygift.collect(0, amount * 2, {"from": giftee})
    ygift.collect(0, amount * 3, {"from": giftee})
    ygift.collect(0, amount * 4, {"from": giftee})

    gift = ygift.gifts(0).dict()
    assert gift["amount"] == 0
    assert token.balanceOf(giftee) == amount * 10
    assert ygift.collectible(0) == 0

    ygift.collect(0, amount * 50, {"from": giftee})
    assert token.balanceOf(giftee) == amount * 10
    assert ygift.collectible(0) == 0

    ygift.collect(0, 0, {"from": giftee})
    assert token.balanceOf(giftee) == amount * 10
    assert ygift.collectible(0) == 0

    ygift.collect(0, amount, {"from": giftee})
    assert token.balanceOf(giftee) == amount * 10
    assert ygift.collectible(0) == 0


def test_cannot_withdraw_not_owned_gift(ygift, token, giftee, chain, receiver):
    amount = Wei("100 ether")
    start = chain[-1].timestamp
    token.approve(ygift, 2 ** 256 - 1)
    ygift.mint(giftee, token, amount * 10, "name", "msg", "url", start, 0)
    with brownie.reverts("yGift: You are not the NFT owner"):
        ygift.collect(0, amount, {"from": receiver})
    with brownie.reverts("yGift: You are not the NFT owner"):
        ygift.collect(0, amount * 10, {"from": receiver})
    with brownie.reverts("yGift: You are not the NFT owner"):
        ygift.collect(0, amount * 100, {"from": receiver})

    ygift.collect(0, amount * 5, {"from": giftee})
    with brownie.reverts("yGift: You are not the NFT owner"):
        ygift.collect(0, amount * 5, {"from": receiver})
