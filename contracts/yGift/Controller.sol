// SPDX-License-Identifier: MIT

pragma solidity ^0.6.4;

contract Controller {
	address public controller;

	constructor() public {
		controller = msg.sender;
	}

	modifier onlyController() {
		require (msg.sender == controller, "Controller: You are not the controller");
		_;
	}

	function setController(address _newController) external onlyController {
		controller = _newController;
	}
}
