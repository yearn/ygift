import brownie
from brownie import Wei


def test_operation(ygift, minter, giftee, token, chain):
    amount = Wei("1000 ether")
    lock = 3600

    # minting a gift should be possible by anyone
    token.approve(ygift, 2 ** 256 - 1, {"from": minter})
    ygift.mint(giftee, token, amount, "url", "name", "msg", lock, {"from": minter})
    gift = ygift.gifts(0).dict()
    gift.pop("createdAt")
    assert gift == {
        "name": "name",
        "minter": minter,
        "recipient": giftee,
        "token": token,
        "amount": amount,
        "imageURL": "url",
        "redeemed": False,
        "lockedDuration": lock,
    }

    # tipping must increase amount
    ygift.tip(0, amount, "tip", {"from": minter})
    gift = ygift.gifts(0).dict()
    assert gift["amount"] == amount * 2
    assert token.balanceOf(ygift) == gift["amount"]

    # unlocking early must fail
    with brownie.reverts():
        ygift.redeem(0, {"from": giftee})

    # unlocking must transfer the nft to recipient
    chain.sleep(lock)
    assert ygift.ownerOf(0) == ygift
    ygift.redeem(0, {"from": giftee})
    assert ygift.ownerOf(0) == giftee

    # tipping should be possible after redeeming
    ygift.tip(0, amount, "tip", {"from": minter})
    assert ygift.gifts(0).dict()["amount"] == amount * 3

    # partial collection should be possible
    ygift.collect(0, amount, {"from": giftee})
    assert token.balanceOf(giftee) == amount
    assert token.balanceOf(ygift) == amount * 2
    assert ygift.gifts(0).dict()["amount"] == amount * 2
