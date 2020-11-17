import brownie
import pytest
from brownie import Wei
from brownie.test import strategy


def test_stateful(ygift, token, chain, giftee, receiver, state_machine):
    class StateMachine:

        # address = strategy('address')
        amount = strategy("uint256", max_value="100 ether")
        start = strategy("uint256", max_value="1000000")
        duration = strategy("uint256", max_value="1500000")

        def __init__(cls, ygift, token, chain, giftee, receiver):
            cls.ygift = ygift
            cls.token = token
            cls.chain = chain
            cls.giftee = giftee
            cls.receiver = receiver

        def setup(self):
            self.token.approve(ygift, 2 ** 256 - 1)

        def rule_mint(self, amount, start, duration):
            time = self.chain[-1].timestamp
            f_start = start + time
            f_duration = duration
            self.ygift.mint(
                self.giftee,
                self.token,
                amount,
                "name",
                "msg",
                "url",
                f_start,
                f_duration,
            )
            gift = ygift.gifts(ygift.totalSupply() - 1).dict()
            assert gift == {
                "token": self.token,
                "name": "name",
                "message": "msg",
                "url": "url",
                "amount": amount,
                "tipped": 0,
                "start": f_start,
                "duration": f_duration,
            }

        # def rule_collect_half(self, amount):
        # 	ygift.collect(ygift.totalSupply() - 1, amount / 2, {'from':self.giftee})
        # 	gift = ygift.gifts(ygift.totalSupply() - 1).dict()
        # 	assert self.token.balanceOf(self.giftee) + gift['amount']  ==  amount

    # state_machine(StateMachine, ygift, token, chain, giftee, receiver)
