// SPDX-License-Identifier: MIT
pragma solidity =0.6.12;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";


contract TestERC1155 is ERC1155("random uri") {
	function mint(uint _id, uint _amount) public {
		_mint(msg.sender, _id, _amount, "");
	}

	function mintBatch(uint[] calldata _ids, uint[] calldata _amounts) public {
		_mintBatch(msg.sender, _ids, _amounts, "");
	}
}