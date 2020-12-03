import pytest


@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass


@pytest.fixture()
def minter(accounts):
    return accounts.at("0x2F0b23f53734252Bda2277357e97e1517d6B042A", force=True)

@pytest.fixture()
def nftholder(accounts):
    return accounts.at("0xf521Bb7437bEc77b0B15286dC3f49A87b9946773", force=True)

@pytest.fixture()
def nftholder2(accounts):
    return accounts.at("0x01bf1d7c5e192313c26414e134584275f46271cf", force=True)


@pytest.fixture()
def giftee(accounts):
    return accounts[1]


@pytest.fixture()
def receiver(accounts):
    return accounts[2]

@pytest.fixture()
def axie(interface):
    return interface.IERC721("0xf5b0a3efb8e8e4c201e2a935f110eaaf3ffecb8d")

@pytest.fixture()
def nfttest(TestNft, minter):
    return TestNft.deploy({"from": minter})

@pytest.fixture()
def nfttest2(TestNft, minter):
    return TestNft.deploy({"from": minter})

@pytest.fixture()
def nfttest3(TestNft, minter):
    return TestNft.deploy({"from": minter})

@pytest.fixture()
def token(interface, minter):
    return interface.ERC20("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", owner=minter)


@pytest.fixture()
def ygift(yGift, minter):
    return yGift.deploy({"from": minter})

@pytest.fixture()
def nftsupport(NFTSupport, minter):
    return NFTSupport.deploy({"from": minter})
