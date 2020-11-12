// SPDX-License-Identifier: MIT

pragma solidity ^0.6.4;

import "../utils/SafeMath.sol";
import "./IERC20.sol";

contract ERC20Mintable is IERC20 {
	using SafeMath for uint256;

	string public _name;
	string public _symbol;
	uint8 public _decimals;

	uint256 public _totalSupply;
	mapping (address => uint256) public _balanceOf;
	mapping (address => mapping (address => uint256)) public _allowance;
	
	function allowance(address owner, address spender) public override view returns(uint256){
	    return _allowance[owner][spender];
	}

	constructor (string memory __name, string memory __symbol, uint8 __decimals) public
	{
		_name = __name;
		_symbol = __symbol;
		_decimals = __decimals;
	}
	
	function decimals() public view returns (uint8) {
        return _decimals;
    }
    
    function symbol() public view returns (string memory) {
        return _symbol;
    }

    /**
     * @dev See {IERC20-totalSupply}.
     */
    function totalSupply() public view override returns (uint256) {
        return _totalSupply;
    }

    /**
     * @dev See {IERC20-balanceOf}.
     */
    function balanceOf(address account) public view override returns (uint256) {
        return _balanceOf[account];
    }


	function approve(address _spender, uint256 _value) public override returns (bool _success) {
		_allowance[msg.sender][_spender] = _value;
		emit Approval(msg.sender, _spender, _value);
		return true;
	}

	function transfer(address _to, uint256 _value) public override returns (bool _success) {
		require(_to != address(0), "Recipient address is null.");
		_balanceOf[msg.sender] = _balanceOf[msg.sender].sub(_value);
		_balanceOf[_to] = _balanceOf[_to].add(_value);
		emit Transfer(msg.sender, _to, _value);
		return true;
	}

	function transferFrom(address _from, address _to, uint256 _value) public override returns (bool _success) {
		require(_to != address(0), "Recipient address is null");
		_balanceOf[_from] = _balanceOf[_from].sub(_value);
		_balanceOf[_to] = _balanceOf[_to].add(_value);
		_allowance[_from][msg.sender] = _allowance[_from][msg.sender].sub(_value);
		emit Transfer(_from, _to, _value);
		return true;
	}

	function mint(address _to, uint256 _amount) public returns (bool)
	{
		_totalSupply = _totalSupply.add(_amount);
		_balanceOf[_to] = _balanceOf[_to].add(_amount);
		emit Transfer(address(0), _to, _amount);
	}
}
