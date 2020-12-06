import brownie
import pytest
from brownie import Wei

def test_transfer_then_collect(nftsupport, nftholder, token, chain, axie, giftee):
    start = chain[-1].timestamp + 1000
    token.approve(nftsupport, 2 ** 256 - 1)
    nftsupport.mint(nftholder, token, 0, "name", "msg", "url", start, 0)
    axie.setApprovalForAll(nftsupport, True, {'from': nftholder})
    assert axie.ownerOf(2815) == nftholder
    nftsupport.sendNftToYgift(axie, 2815, 1, {'from': nftholder})
    assert axie.ownerOf(2815) == nftsupport
    tokenId = 1
    assert nftsupport.numberOfDifferentNftsInGift(tokenId) == 1
    assert nftsupport.nftContractInGift(tokenId, 0) == axie
    assert nftsupport.balanceOfOneNft(tokenId, axie) == 1
    assert nftsupport.getIdOfNftContractInGift(tokenId, axie, 0) == 2815
    assert nftsupport.getIndexOfNftIdInGift(tokenId, axie, 2815) == 0
    assert nftsupport.ownerOfChild(axie, 2815) == nftholder
    nftsupport.collectNftFromYgift(axie, 2815, tokenId, {'from': nftholder})
    assert axie.ownerOf(2815) == nftholder

def test_transfer_then_revert_collect(nftsupport, nftholder, token, chain, axie, giftee):
    start = chain[-1].timestamp + 1000
    token.approve(nftsupport, 2 ** 256 - 1)
    nftsupport.mint(nftholder, token, 0, "name", "msg", "url", start, 0)
    axie.setApprovalForAll(nftsupport, True, {'from': nftholder})
    tokenId = 1
    assert axie.ownerOf(2815) == nftholder
    nftsupport.sendNftToYgift(axie, 2815, tokenId, {'from': nftholder})
    assert axie.ownerOf(2815) == nftsupport
    with brownie.reverts("NFTSupport: You are not the NFT owner"):
        nftsupport.collectNftFromYgift(axie, 2815, tokenId, {'from': giftee})

def test_transfer_many(nftsupport, nftholder, nftholder2, token, chain, axie, giftee):
    start = chain[-1].timestamp + 1000
    token.approve(nftsupport, 2 ** 256 - 1)
    nftsupport.mint(nftholder, token, 0, "name", "msg", "url", start, 0)
    tokenId = 1
    axie.setApprovalForAll(nftsupport, True, {'from': nftholder})
    axie.setApprovalForAll(nftsupport, True, {'from': nftholder2})
    nftsupport.sendNftToYgift(axie, 2815, tokenId, {'from': nftholder})
    assert axie.ownerOf(2815) == nftsupport
    assert nftsupport.ownerOfChild(axie, 2815) == nftholder
    nftsupport.sendNftToYgift(axie, 2544, tokenId, {'from': nftholder})
    assert axie.ownerOf(2544) == nftsupport
    assert nftsupport.ownerOfChild(axie, 2544) == nftholder
    nftsupport.sendNftToYgift(axie, 1, tokenId, {'from': nftholder2})
    assert axie.ownerOf(1) == nftsupport
    assert nftsupport.ownerOfChild(axie, 1) == nftholder
    nftsupport.sendNftToYgift(axie, 2, tokenId, {'from': nftholder2})
    assert axie.ownerOf(2) == nftsupport
    assert nftsupport.ownerOfChild(axie, 2) == nftholder
    with brownie.reverts("NFTSupport: You are not the NFT owner"):
        nftsupport.collectNftFromYgift(axie, 2815, tokenId, {'from': giftee})

    assert nftsupport.numberOfDifferentNftsInGift(tokenId) == 1
    assert nftsupport.nftContractInGift(tokenId, 0) == axie
    assert nftsupport.balanceOfOneNft(tokenId, axie) == 4
    assert nftsupport.getIdOfNftContractInGift(tokenId, axie, 0) == 2815
    assert nftsupport.getIdOfNftContractInGift(tokenId, axie, 2) == 1
    assert nftsupport.getIndexOfNftIdInGift(tokenId, axie, 2544) == 1
    assert nftsupport.getIndexOfNftIdInGift(tokenId, axie, 2) == 3

    nftsupport.collectNftFromYgift(axie, 2815, tokenId, {'from': nftholder})
    assert axie.ownerOf(2815) == nftholder
    nftsupport.collectNftFromYgift(axie, 2544, tokenId, {'from': nftholder})
    assert axie.ownerOf(2544) == nftholder
    nftsupport.collectNftFromYgift(axie, 1, tokenId, {'from': nftholder})
    assert axie.ownerOf(1) == nftholder
    nftsupport.collectNftFromYgift(axie, 2, tokenId, {'from': nftholder})
    assert axie.ownerOf(2) == nftholder

def test_collect_when_2_nft_in_contract(nftsupport, nftholder, token, chain, axie, giftee):
    start = chain[-1].timestamp + 1000
    token.approve(nftsupport, 2 ** 256 - 1)
    nftsupport.mint(nftholder, token, 0, "name", "msg", "url", start, 0)
    nftsupport.mint(nftholder, token, 0, "name", "msg", "url", start, 0)
    axie.setApprovalForAll(nftsupport, True, {'from': nftholder})
    nftsupport.sendNftToYgift(axie, 2815, 1, {'from': nftholder})
    nftsupport.sendNftToYgift(axie, 2544, 2, {'from': nftholder})
    with brownie.reverts("NFTSupport: NFT ID is not attached to yGift ID"):
        nftsupport.collectNftFromYgift(axie, 2544, 1, {'from': nftholder})

def test_many_different_nfts(nftsupport, nftholder, token, chain, nfttest, nfttest2, nfttest3, giftee):
    start = chain[-1].timestamp + 1000
    token.approve(nftsupport, 2 ** 256 - 1)
    nftsupport.mint(nftholder, token, 0, "name", "msg", "url", start, 0)
    nfttest.setApprovalForAll(nftsupport, True, {'from': nftholder})
    nfttest2.setApprovalForAll(nftsupport, True, {'from': nftholder})
    nfttest3.setApprovalForAll(nftsupport, True, {'from': nftholder})
    tokenId = 1
    for i in range(3):
        nfttest.mint({'from': nftholder})
        nftsupport.sendNftToYgift(nfttest, i, tokenId, {'from': nftholder})

    for j in range(4):
        nfttest2.mint({'from': nftholder})
        nftsupport.sendNftToYgift(nfttest2, j, tokenId, {'from': nftholder})

    for k in range(5):
        nfttest3.mint({'from': nftholder})
        nftsupport.sendNftToYgift(nfttest3, k, tokenId, {'from': nftholder})
    
    assert nftsupport.numberOfDifferentNftsInGift(tokenId) == 3
    assert nftsupport.nftContractInGift(tokenId, 0) == nfttest
    assert nftsupport.nftContractInGift(tokenId, 1) == nfttest2
    assert nftsupport.nftContractInGift(tokenId, 2) == nfttest3
    assert nftsupport.balanceOfOneNft(tokenId, nfttest) == 3
    assert nftsupport.balanceOfOneNft(tokenId, nfttest2) == 4
    assert nftsupport.balanceOfOneNft(tokenId, nfttest3) == 5
    assert nftsupport.getIdOfNftContractInGift(tokenId, nfttest, 0) == 0
    assert nftsupport.getIdOfNftContractInGift(tokenId, nfttest2, 2) == 2
    assert nftsupport.getIdOfNftContractInGift(tokenId, nfttest3, 4) == 4
    assert nftsupport.getIndexOfNftIdInGift(tokenId, nfttest, 2) == 2
    assert nftsupport.getIndexOfNftIdInGift(tokenId, nfttest2, 1) == 1
    assert nftsupport.getIndexOfNftIdInGift(tokenId, nfttest3, 0) == 0

    for i in range(3):
        nftsupport.collectNftFromYgift(nfttest, i, tokenId, {'from': nftholder})

    for j in range(4):
        nftsupport.collectNftFromYgift(nfttest2, j, tokenId, {'from': nftholder})

    for k in range(5):
        nftsupport.collectNftFromYgift(nfttest3, k, tokenId, {'from': nftholder})

    assert nftsupport.numberOfDifferentNftsInGift(tokenId) == 0

def test_recursive_gifts_axie(nftsupport, nftholder, axie, token, chain):
    axie.setApprovalForAll(nftsupport, True, {'from':nftholder})
    start = chain[-1].timestamp
    nftsupport.setApprovalForAll(nftsupport, True, {'from':nftholder})
    nftsupport.mint(nftholder, token, 0, "name", "msg", "url", start, 0)
    nftsupport.mint(nftholder, token, 0, "name", "msg", "url", start, 0)
    nftsupport.mint(nftholder, token, 0, "name", "msg", "url", start, 0)
    nftsupport.sendNftToYgift(nftsupport, 1, 2, {'from':nftholder})
    nftsupport.sendNftToYgift(nftsupport, 2, 3, {'from':nftholder})
    nftsupport.sendNftToYgift(axie, 2815, 1,{'from':nftholder})
    assert nftsupport.ownerOfChild(axie, 2815) == nftsupport
    assert nftsupport.rootOwnerOfChild(axie, 2815) == nftholder
    assert nftsupport.rootOwnerOfChild(nftsupport, 1) == nftholder
    assert nftsupport.rootOwnerOfChild(nftsupport, 2) == nftholder