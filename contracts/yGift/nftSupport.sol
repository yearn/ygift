// SPDX-License-Identifier: MIT
pragma solidity =0.6.12;

import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC1155/IERC1155.sol";
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

	struct ERC1155Data {
		address[] erc1155Contracts;
		mapping(address => uint[]) erc1155Tokens;
		mapping(address => mapping(uint => uint)) erc1155TokenValue;
		mapping(address => mapping(uint => uint)) erc1155TokenIndex;
	}

	mapping(uint => NFTData) nftData;
	mapping(uint => ERC1155Data) erc1155Data;
	mapping(address => mapping(uint => uint)) public nftTokenToYGift;

	event nftAttached(address indexed nftContract, uint indexed nftId, uint indexed giftId);
	event nftDetached(address indexed nftContract, uint indexed nftId, uint indexed giftId);

	event erc1155Attached(address indexed erc1155Contract, uint indexed erc1155Id, uint erc1155Tokenvalue, uint indexed giftId);
	event erc1155Detached(address indexed erc1155Contract, uint indexed erc1155Id, uint erc1155Tokenvalue, uint indexed giftId);

	event erc1155BatchAttached(address indexed erc1155Contract, uint[] erc1155Ids, uint[] erc1155Tokensvalue, uint indexed giftId);
	event erc1155BatchDetached(address indexed erc1155Contract, uint[] erc1155Ids, uint[] erc1155Tokensvalue, uint indexed giftId);

	function _indexOfAddressInArray(address[] memory _data, address _address) internal pure returns(uint) {
		for(uint i = 0; i < _data.length; i++)
			if (_data[i] == _address)
				return i;
		return uint(-1);
	}

	function _indexOfUintInArray(uint[] memory _data, uint _index) internal pure returns(uint) {
		for(uint i = 0; i < _data.length; i++)
			if (_data[i] == _index)
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
		uint index = nftData[_tokenId].nftTokenIndex[_nftContract][_nftId];
		require (index != 0, "NFTSupport: nft is not indexed");
		return index - 1;
	}

	function numberOfDifferentErc1155InGift(uint _tokenId) public view returns (uint) {
		return erc1155Data[_tokenId].erc1155Contracts.length;
	}

	function erc1155ContractInGift(uint _tokenId, uint _index) public view returns (address) {
		return erc1155Data[_tokenId].erc1155Contracts[_index];
	}

	function amountOfErc1155TokensInGift(uint _tokenId, address _erc1155Contract) public view returns (uint) {
		return erc1155Data[_tokenId].erc1155Tokens[_erc1155Contract].length;
	}

	function getErc1155TokenIdInGift(uint _tokenId, address _erc1155Contract, uint _erc1155tokenId) public view returns (uint) {
		return erc1155Data[_tokenId].erc1155Tokens[_erc1155Contract][_erc1155tokenId];
	}

	function getErc1155TokenIndexInGift(uint _tokenId, address _erc1155Contract, uint _erc1155TokenId) public view returns (uint) {
		uint index = erc1155Data[_tokenId].erc1155TokenIndex[_erc1155Contract][_erc1155TokenId];
		require (index != 0, "ERC1155Support: Index cannot be 0");
		return index - 1; 
	}

	function getValueOfErc1155TokenInGift(uint _tokenId, address _erc1155Contract, uint _erc1155TokenId) public view returns (uint) {
		return erc1155Data[_tokenId].erc1155TokenValue[_erc1155Contract][_erc1155TokenId];
	}

	function sendNftToYgift(address _nftContract, uint _nftId, uint _yGiftId) public {
		require (_yGiftId != 0, "NFTSupport: yGift id cannot be 0");
		require (_yGiftId < totalSupply() + 1, "NFTSupport: yGift id is out of range");

		nftTokenToYGift[_nftContract][_nftId] = _yGiftId;
		NFTData storage data = nftData[_yGiftId];
		if (_indexOfAddressInArray(data.nftContracts, _nftContract) == uint(-1))
			data.nftContracts.push(_nftContract);
		uint index = data.nftTokens[_nftContract].length;
		// we add 1 to use 0 as error in indexing
		data.nftTokenIndex[_nftContract][_nftId] = index + 1;
		data.nftTokens[_nftContract].push(_nftId);

		IERC721(_nftContract).safeTransferFrom(msg.sender, address(this), _nftId);
		emit nftAttached(_nftContract, _nftId, _yGiftId);
	}

	function collectNftFromYgift(address _nftContract, uint _nftId, uint _yGiftId) public {
		require(_isApprovedOrOwner(msg.sender, _yGiftId), "NFTSupport: You are not the NFT owner");
		require(nftTokenToYGift[_nftContract][_nftId] == _yGiftId, "NFTSupport: NFT ID is not attached to yGift ID");
		NFTData storage data = nftData[_yGiftId];
		require(data.nftTokenIndex[_nftContract][_nftId] != 0, "NFTSupport: index cannot be 0");

		// index offset removed
		uint index = data.nftTokenIndex[_nftContract][_nftId] - 1;
		uint nftLength = data.nftTokens[_nftContract].length;
		uint lastId = data.nftTokens[_nftContract][nftLength - 1];

		data.nftTokens[_nftContract][index] = lastId;
		data.nftTokenIndex[_nftContract][lastId] = index + 1;
		data.nftTokens[_nftContract].pop();
		if (nftLength == 1) {
			uint contractLength = data.nftContracts.length;
			uint contractIndex = _indexOfAddressInArray(data.nftContracts, _nftContract);
			data.nftContracts[contractIndex] = data.nftContracts[contractLength - 1];
			data.nftContracts.pop();
		}
		delete nftTokenToYGift[_nftContract][_nftId];
		delete data.nftTokenIndex[_nftContract][_nftId];
		IERC721(_nftContract).safeTransferFrom(address(this), msg.sender, _nftId);
		emit nftDetached(_nftContract, _nftId, _yGiftId);
	}

	function sendErc1155ToYgift(address _erc1155Contract, uint _erc1155TokenId, uint _erc1155TokenValue, uint _yGiftId) public {
		require (_yGiftId != 0, "NFTSupport: yGift id cannot be 0");
		require (_yGiftId < totalSupply() + 1, "NFTSupport: yGift id is out of range");	

		ERC1155Data storage data = erc1155Data[_yGiftId];
		uint indexToken =  data.erc1155TokenIndex[_erc1155Contract][_erc1155TokenId];
		if (indexToken != 0)
			data.erc1155TokenValue[_erc1155Contract][_erc1155TokenId] = data.erc1155TokenValue[_erc1155Contract][_erc1155TokenId].add(_erc1155TokenValue);
		else {
			if (_indexOfAddressInArray(data.erc1155Contracts, _erc1155Contract) == uint(-1))
				data.erc1155Contracts.push(_erc1155Contract);
			uint index = data.erc1155Tokens[_erc1155Contract].length;
			// we add 1 to use 0 as error in indexing
			data.erc1155TokenIndex[_erc1155Contract][_erc1155TokenId] = index + 1;
			data.erc1155Tokens[_erc1155Contract].push(_erc1155TokenId);
			data.erc1155TokenValue[_erc1155Contract][_erc1155TokenId] = _erc1155TokenValue;
		}

		IERC1155(_erc1155Contract).safeTransferFrom(msg.sender, address(this), _erc1155TokenId, _erc1155TokenValue, "");
		emit erc1155Attached(_erc1155Contract, _erc1155TokenId, _erc1155TokenValue, _yGiftId);
	}

	function collectErc1155FromYgift(address _erc1155Contract, uint _erc1155TokenId, uint _erc1155TokenValue, uint _yGiftId) public {
		require(_isApprovedOrOwner(msg.sender, _yGiftId), "NFTSupport: You are not the NFT owner");

		ERC1155Data storage data = erc1155Data[_yGiftId];
		require(data.erc1155TokenIndex[_erc1155Contract][_erc1155TokenId] != 0, "ERC1155Support: YGift does not have tokenId indexed from given address");
		// remove offset
		uint tokenIndex = data.erc1155TokenIndex[_erc1155Contract][_erc1155TokenId] - 1;
		uint currentTokenValue = data.erc1155TokenValue[_erc1155Contract][_erc1155TokenId];
		require(_erc1155TokenValue <= currentTokenValue, "ERC1155Support: yGift doesn't have sufficient erc1155 token value");
		if (_erc1155TokenValue < currentTokenValue)
			data.erc1155TokenValue[_erc1155Contract][_erc1155TokenId] = data.erc1155TokenValue[_erc1155Contract][_erc1155TokenId].sub(_erc1155TokenValue);
		else {
			uint tokenLength = data.erc1155Tokens[_erc1155Contract].length;
			uint lastTokenId = data.erc1155Tokens[_erc1155Contract][tokenLength - 1];
			delete data.erc1155TokenValue[_erc1155Contract][_erc1155TokenId];
			delete data.erc1155TokenIndex[_erc1155Contract][_erc1155TokenId];
			data.erc1155Tokens[_erc1155Contract][tokenIndex] = lastTokenId;
			if (tokenIndex != lastTokenId)
				data.erc1155TokenIndex[_erc1155Contract][lastTokenId] = tokenIndex + 1;
			data.erc1155Tokens[_erc1155Contract].pop();
			if (tokenLength == 1) {
				uint contractLength = data.erc1155Contracts.length;
				uint contractIndex = _indexOfAddressInArray(data.erc1155Contracts, _erc1155Contract);
				data.erc1155Contracts[contractIndex] = data.erc1155Contracts[contractLength - 1];
				data.erc1155Contracts.pop();
			}
		}
		IERC1155(_erc1155Contract).safeTransferFrom(address(this), msg.sender, _erc1155TokenId, _erc1155TokenValue, "");
		emit erc1155Detached(_erc1155Contract, _erc1155TokenId, _erc1155TokenValue, _yGiftId);
	}

	function sendBatchErc1155ToYgift(address _erc1155Contract, uint[] calldata _erc1155TokensId, uint[] calldata _erc1155TokensValue, uint _yGiftId) public {
		require (_yGiftId != 0, "NFTSupport: yGift id cannot be 0");
		require (_yGiftId < totalSupply() + 1, "NFTSupport: yGift id is out of range");
		require(_erc1155TokensId.length == _erc1155TokensValue.length, "ERC1155Support: token and value array not same size.");

		ERC1155Data storage data = erc1155Data[_yGiftId];
		if (_indexOfAddressInArray(data.erc1155Contracts, _erc1155Contract) == uint(-1))
			data.erc1155Contracts.push(_erc1155Contract);
		for (uint i = 0; i < _erc1155TokensId.length; i++){
			uint indexToken =  data.erc1155TokenIndex[_erc1155Contract][_erc1155TokensId[i]];
			if (indexToken != 0)
				data.erc1155TokenValue[_erc1155Contract][_erc1155TokensId[i]] = data.erc1155TokenValue[_erc1155Contract][_erc1155TokensId[i]].add(_erc1155TokensValue[i]);
			else {
				uint index = data.erc1155Tokens[_erc1155Contract].length;
				// we add 1 to use 0 as error in indexing
				data.erc1155TokenIndex[_erc1155Contract][_erc1155TokensId[i]] = index + 1;
				data.erc1155Tokens[_erc1155Contract].push(_erc1155TokensId[i]);
				data.erc1155TokenValue[_erc1155Contract][_erc1155TokensId[i]] = _erc1155TokensValue[i];
			}
		}

		IERC1155(_erc1155Contract).safeBatchTransferFrom(msg.sender, address(this), _erc1155TokensId, _erc1155TokensValue, "");
		emit erc1155BatchAttached(_erc1155Contract, _erc1155TokensId, _erc1155TokensValue, _yGiftId);
	}

	function collectBatchErc1155FromYgift(address _erc1155Contract, uint[] calldata _erc1155TokensId, uint[] calldata _erc1155TokensValue, uint _yGiftId) public {
		require(_isApprovedOrOwner(msg.sender, _yGiftId), "NFTSupport: You are not the NFT owner");
		require(_erc1155TokensId.length == _erc1155TokensValue.length, "ERC1155Support: token and value array not same size.");

		ERC1155Data storage data = erc1155Data[_yGiftId];
		for (uint i = 0; i < _erc1155TokensId.length; i++){
			require(data.erc1155TokenIndex[_erc1155Contract][_erc1155TokensId[i]] != 0, "ERC1155Support: YGift does not have tokenId indexed from given address");
			// remove offset
			uint tokenIndex = data.erc1155TokenIndex[_erc1155Contract][_erc1155TokensId[i]] - 1;
			// uint tokenId = data.erc1155Tokens[_erc1155Contract][tokenIndex];
			uint currentTokenValue = data.erc1155TokenValue[_erc1155Contract][_erc1155TokensId[i]];
			require(_erc1155TokensValue[i] <= currentTokenValue, "ERC1155Support: yGift doesn't have sufficient erc1155 token value");
			if (_erc1155TokensValue[i] < currentTokenValue)
				data.erc1155TokenValue[_erc1155Contract][_erc1155TokensId[i]] = data.erc1155TokenValue[_erc1155Contract][_erc1155TokensId[i]].sub(_erc1155TokensValue[i]);
			else {
				uint tokenLength = data.erc1155Tokens[_erc1155Contract].length;
				uint lastTokenId = data.erc1155Tokens[_erc1155Contract][tokenLength - 1];
				delete data.erc1155TokenValue[_erc1155Contract][_erc1155TokensId[i]];
				delete data.erc1155TokenIndex[_erc1155Contract][_erc1155TokensId[i]];
				data.erc1155Tokens[_erc1155Contract][tokenIndex] = lastTokenId;
				if (tokenIndex != lastTokenId)
					data.erc1155TokenIndex[_erc1155Contract][lastTokenId] = tokenIndex + 1;
				data.erc1155Tokens[_erc1155Contract].pop();
				if (tokenLength == 1) {
					uint contractLength = data.erc1155Contracts.length;
					uint contractIndex = _indexOfAddressInArray(data.erc1155Contracts, _erc1155Contract);
					data.erc1155Contracts[contractIndex] = data.erc1155Contracts[contractLength - 1];
					data.erc1155Contracts.pop();
				}
			}
		}
		IERC1155(_erc1155Contract).safeBatchTransferFrom(address(this), msg.sender, _erc1155TokensId, _erc1155TokensValue, "");
		emit erc1155BatchDetached(_erc1155Contract, _erc1155TokensId, _erc1155TokensValue, _yGiftId);
	}

	function onERC721Received(address operator, address from, uint256 tokenId, bytes calldata data)
    external pure returns (bytes4)  {
		return bytes4(keccak256("onERC721Received(address,address,uint256,bytes)"));
	}

	function onERC721Received(address _from, uint256 _tokenId, bytes calldata _data) external pure returns (bytes4) {
		return bytes4(keccak256("onERC721Received(address,uint256,bytes)"));
	}

	function onERC1155Received(address _operator, address _from, uint256 _id, uint256 _value, bytes calldata _data) external returns(bytes4) {
		return NFTSupport.onERC1155Received.selector;
	}

	function onERC1155BatchReceived(address _operator, address _from, uint256[] calldata _ids, uint256[] calldata _values, bytes calldata _data) external returns(bytes4) {
		return NFTSupport.onERC1155BatchReceived.selector;
	}
}