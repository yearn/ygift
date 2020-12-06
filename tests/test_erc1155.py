import brownie
import pytest
from brownie import Wei

def test_transfer_then_collect(nftsupport, nftholder, token, erc1155test, chain, giftee):
    start = chain[-1].timestamp + 1000
    token.approve(nftsupport, 2 ** 256 - 1)
    nftsupport.mint(nftholder, token, 0, "name", "msg", "url", start, 0)
    nftsupport.mint(giftee, token, 0, "name", "msg", "url", start, 0)
    erc1155test.setApprovalForAll(nftsupport, True, {'from': nftholder})
    erc1155test.mintBatch([0, 2, 4], [100, 200, 300], {'from': nftholder})
    ballArr = erc1155test.balanceOfBatch([nftholder, nftholder, nftholder], [0, 2, 4])
    assert ballArr[0] == 100
    assert ballArr[1] == 200
    assert ballArr[2] == 300
    nftsupport.sendErc1155ToYgift(erc1155test, 0, 50, 1, {'from': nftholder})
    assert erc1155test.balanceOf(nftsupport, 0) == 50
    with brownie.reverts("ERC1155Support: YGift does not have tokenId indexed from given address"):
        nftsupport.collectErc1155FromYgift(erc1155test, 0, 50, 2, {'from': giftee})
    nftsupport.collectErc1155FromYgift(erc1155test, 0, 50, 1, {'from': nftholder})
    assert erc1155test.balanceOf(nftholder, 0) == 100
    nftsupport.sendBatchErc1155ToYgift(erc1155test, [0, 2, 4], [50, 100, 150], 1, {'from': nftholder})
    ballArr = erc1155test.balanceOfBatch([nftsupport, nftsupport, nftsupport], [0, 2, 4])
    assert ballArr[0] == 50
    assert ballArr[1] == 100
    assert ballArr[2] == 150
    assert nftsupport.amountOfErc1155TokensInGift(1, erc1155test) == 3
    nftsupport.collectBatchErc1155FromYgift(erc1155test, [0, 2, 4], [50, 100, 150], 1, {'from': nftholder})
    assert nftsupport.amountOfErc1155TokensInGift(1, erc1155test) == 0
    ballArr = erc1155test.balanceOfBatch([nftholder, nftholder, nftholder], [0, 2, 4])
    assert ballArr[0] == 100
    assert ballArr[1] == 200
    assert ballArr[2] == 300

# def som():
#     nftsupport = NFTSupport.deploy({"from": accounts[0]})
#     nftholder = accounts.at("0xf521Bb7437bEc77b0B15286dC3f49A87b9946773", force=True)
#     token = interface.ERC20("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", owner=accounts[0])
#     erc1155test = TestERC1155.deploy({"from": nftholder})
#     giftee = accounts[0]
#     start = chain[-1].timestamp + 1000
#     token.approve(nftsupport, 2 ** 256 - 1)
#     nftsupport.mint(nftholder, token, 0, "name", "msg", "url", start, 0)
#     nftsupport.mint(giftee, token, 0, "name", "msg", "url", start, 0)
#     erc1155test.setApprovalForAll(nftsupport, True, {'from': nftholder})
#     erc1155test.mintBatch([0, 2, 4], [100, 200, 300], {'from': nftholder})
#     nftsupport.sendErc1155ToYgift(erc1155test, 0, 50, 1, {'from': nftholder})
#     nftsupport.collectErc1155FromYgift(erc1155test, 0, 50, 1, {'from': nftholder})


#     erc1155test.setApprovalForAll(nftsupport, True, {'from': nftholder})
#     erc1155test.mintBatch([0, 2, 4], [100, 200, 300], {'from': nftholder})
#     # nftsupport.sendBatchErc1155ToYgift(erc1155test, [0, 2, 4], [50, 100, 150], 1, {'from': nftholder})
#     nftsupport.sendBatchErc1155ToYgift(erc1155test, [0], [50], 1, {'from': nftholder})

# nftsupport.numberOfDifferentErc1155InGift(1)
# nftsupport.amountOfErc1155TokensInGift(1, erc1155test)
# nftsupport.getValueOfErc1155TokenInGift(1, erc1155test, 0)
# nftsupport.getErc1155TokenIndexInGift(1, erc1155test, 0)