import brownie


def test_controller(ygift, controller, gifter, token):
    assert ygift.symbol() == "yGIFT"
    assert ygift.controller() == controller

    ygift.addTokens([token])
    assert ygift.supportedTokens(token)

    assert not ygift.whitelistedMinters(controller)

    ygift.addMinter([controller])
    assert ygift.whitelistedMinters(controller)

    ygift.removeMinter([controller, gifter])
    assert not ygift.whitelistedMinters(controller)

    with brownie.reverts():
        ygift.addMinter([gifter], {"from": gifter})

    ygift.setController(gifter)
    assert ygift.controller() == gifter

    with brownie.reverts():
        ygift.setController(controller)
