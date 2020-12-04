// SPDX-License-Identifier: MIT
pragma solidity =0.6.12;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import "@openzeppelin/contracts/math/SafeMath.sol";

import "./yGift.sol";

contract NFTSupport is yGift{

	struct NFTData {
		address[] nftContracts;
		mapping(address => uint[]) nftTokens;
		mapping(address => mapping(uint => uint)) nftTokenIndex;
	}

	mapping(uint => NFTData) nftData;
	mapping(address => mapping(uint => uint)) public nftTokenToYGift;

	event nftAttached(address indexed nftContract, uint indexed nftId, uint indexed giftId);
	event nftDetached(address indexed nftContract, uint indexed nftId, uint indexed giftId);

	function _indexOfAddressInArray(NFTData memory _data, address _address) internal pure returns(uint) {
		for(uint i = 0; i < _data.nftContracts.length; i++)
			if (_data.nftContracts[i] == _address)
				return i;
		return uint(-1);
	}

	function ownerOfChild(address _nftContract, uint _nftId) public view returns (address) {
		uint tokenId = nftTokenToYGift[_nftContract][_nftId];
		require (tokenId > 0, "NFTSupport: tokenId owner cannot be 0");
		return ownerOf(tokenId);
	}

	function rootOwnerOfChild(address _nftContract, uint _nftId) public view returns (address) {
		uint tokenId = nftTokenToYGift[_nftContract][_nftId];
		require (tokenId > 0, "NFTSupport: tokenId owner cannot be 0");
		address owner = ownerOf(tokenId);
		while (owner == address(this)){
			tokenId = nftTokenToYGift[owner][tokenId];
			require (tokenId > 0, "NFTSupport: tokenId owner cannot be 0");
			owner = ownerOf(tokenId);
		}
		return owner;
	}

	function numberOfDifferentNftsInGift(uint _tokenId) public view returns (uint) {
		return nftData[_tokenId].nftContracts.length;
	}

	function nftContractInGift(uint _tokenId, uint _index) public view returns (address) {
		return nftData[_tokenId].nftContracts[_index];
	}

	function balanceOfOneNft(uint _tokenId, address _nftContract) public view returns (uint) {
		return nftData[_tokenId].nftTokens[_nftContract].length;
	}

	function getIdOfNftContractInGift(uint _tokenId, address _nftContract, uint _index) public view returns (uint) {
		return nftData[_tokenId].nftTokens[_nftContract][_index];
	}

	function getIndexOfNftIdInGift(uint _tokenId, address _nftContract, uint _nftId) public view returns (uint) {
		return nftData[_tokenId].nftTokenIndex[_nftContract][_nftId];
	}

	function sendNftToYgift(address _nftContract, uint _nftId, uint _yGiftId) public {
		require (_yGiftId < totalSupply() + 1, "NFTSupport: yGift id is out of range");

		nftTokenToYGift[_nftContract][_nftId] = _yGiftId;
		NFTData storage data = nftData[_yGiftId];
		if (_indexOfAddressInArray(data, _nftContract) == uint(-1))
			data.nftContracts.push(_nftContract);
		uint index = data.nftTokens[_nftContract].length;
		data.nftTokenIndex[_nftContract][_nftId] = index;
		data.nftTokens[_nftContract].push(_nftId);

		IERC721(_nftContract).safeTransferFrom(msg.sender, address(this), _nftId);
		emit nftAttached(_nftContract, _nftId, _yGiftId);
	}

	function collectNftFromYgift(address _nftContract, uint _nftId, uint _yGiftId) public {
		require(_isApprovedOrOwner(msg.sender, _yGiftId), "NFTSupport: You are not the NFT owner");
		require(nftTokenToYGift[_nftContract][_nftId] == _yGiftId, "NFTSupport: NFT ID is not attached to yGift ID");

		NFTData storage data = nftData[_yGiftId];

		uint index = data.nftTokenIndex[_nftContract][_nftId];
		uint nftLength = data.nftTokens[_nftContract].length;
		uint lastId = data.nftTokens[_nftContract][nftLength - 1];

		data.nftTokens[_nftContract][index] = lastId;
		data.nftTokenIndex[_nftContract][lastId] = index;
		data.nftTokens[_nftContract].pop();
		if (nftLength == 1) {
			uint contractLength = data.nftContracts.length;
			uint contractIndex = _indexOfAddressInArray(data, _nftContract);
			data.nftContracts[contractIndex] = data.nftContracts[contractLength - 1];
			data.nftContracts.pop();
		}
		delete nftTokenToYGift[_nftContract][_nftId];
		delete data.nftTokenIndex[_nftContract][_nftId];
		IERC721(_nftContract).safeTransferFrom(address(this), msg.sender, _nftId);
		emit nftDetached(_nftContract, _nftId, _yGiftId);
	}

	function onERC721Received(address operator, address from, uint256 tokenId, bytes calldata data)
    external pure returns (bytes4)  {
		return bytes4(keccak256("onERC721Received(address,address,uint256,bytes)"));
	}

	function onERC721Received(address _from, uint256 _tokenId, bytes calldata _data) external pure returns (bytes4) {
		return bytes4(keccak256("onERC721Received(address,uint256,bytes)"));
	}
}