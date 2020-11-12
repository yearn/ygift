// SPDX-License-Identifier: MIT

pragma solidity ^0.6.4;

contract Controller {
	address controller;

	mapping(address => bool) whitelistedMinters;

	constructor() public {
		controller = msg.sender;
	}

	modifier onlyController() {
		require (msg.sender == controller, "Controller: You are not the controller");
		_;
	}

	modifier onlyWhitelisted() {
		require(msg.sender == controller || whitelistedMinters[msg.sender],
		"Controller: You are not allowed to mint");
		_;
	}

	function setController(address _newController) external onlyController {
		controller = _newController;
	}

	function addMinter(address[] calldata _minters) external onlyController {
		for (uint256 i = 0; i < _minters.length; i++)
			whitelistedMinters[_minters[i]] = true;
	}

	function removeMinter(address[] calldata _minters) external onlyController {
		for (uint256 i = 0; i < _minters.length; i++)
			whitelistedMinters[_minters[i]] = false;
	}
}