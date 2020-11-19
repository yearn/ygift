import brownie
from brownie.test import strategy
from random import randrange


class StateMachine:

    st_amount = strategy("uint256", max_value="500 ether")
    st_sleep = strategy("uint256", max_value=2000)

    def __init__(cls, ygift, token, chain, giftee, receiver):
        cls.ygift = ygift
        cls.token = token
        cls.chain = chain
        cls.giftee = giftee
        cls.receiver = receiver

    def setup(self):
        self.token.approve(self.ygift, 2 ** 256 - 1)

    def initialize(self):
        print("  mint()")
        start = self.chain[-1].timestamp + 1000
        duration = 1000
        amount = "100 ether"
        self.ygift.mint(
            self.giftee,
            self.token,
            amount,
            "name",
            "msg",
            "url",
            start,
            duration,
        )

    def rule_tip(self):
        print("  tip()")
        num_gifts = self.ygift.totalSupply()
        if not num_gifts:
            return
        gift = randrange(num_gifts)
        self.ygift.tip(gift, "50 ether", "tip")

    def rule_transfer(self):
        print("  transferFrom()")
        if not self.ygift.totalSupply():
            return
        if self.ygift.ownerOf(0) == self.giftee:
            self.ygift.transferFrom(
                self.giftee, self.receiver, 0, {"from": self.giftee}
            )
        else:
            with brownie.reverts("ERC721: transfer caller is not owner nor approved"):
                self.ygift.transferFrom(
                    self.giftee, self.receiver, 0, {"from": self.giftee}
                )

    def rule_collect(self, amount="st_amount", sleep="st_sleep"):
        print("  collect()")
        num_gifts = self.ygift.totalSupply()
        if not num_gifts or amount == 0:
            return
        gift = randrange(num_gifts)

        if self.ygift.ownerOf(0) != self.giftee:
            with brownie.reverts("yGift: You are not the NFT owner"):
                self.ygift.collect(gift, amount, {"from": self.giftee})
            return

        giftee_before = self.token.balanceOf(self.giftee)
        ygift_before = self.token.balanceOf(self.ygift)

        self.chain.sleep(sleep)
        self.chain.mine()
        collectible = self.ygift.collectible(0)
        if self.chain[-1].timestamp < self.ygift.gifts(0).dict()["start"]:
            with brownie.reverts("yGift: Rewards still vesting"):
                self.ygift.collect(gift, amount, {"from": self.giftee})
            return

        self.ygift.collect(gift, amount, {"from": self.giftee})
        amount = min(amount, collectible)
        assert self.token.balanceOf(self.giftee) == giftee_before + amount
        assert self.token.balanceOf(self.ygift) == ygift_before - amount


def test_stateful(ygift, token, chain, giftee, receiver, state_machine):
    state_machine(StateMachine, ygift, token, chain, giftee, receiver)
