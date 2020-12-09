// SPDX-License-Identifier: MIT
pragma solidity =0.6.12;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";


contract TestNft is ERC721("This is a test", "TEST"){
	function mint() public {
		uint _id = totalSupply();
		_safeMint(msg.sender, _id);
	}
}