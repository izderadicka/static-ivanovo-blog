+++
title = "Ethereum local playground"
path = "/ethereum-local-playground/"
date = "2017-08-19T11:44:08"
include_in_feeds = true
[extra]
wordpress_id = 1617
kind = "post"
node_key = "1617"
author = "admin"
source_url = "http://zderadicka.eu/ethereum-local-playground/"
source_guid = "http://zderadicka.eu/?p=1617"
source_date_gmt = "2017-08-19 10:44:08"
categories = ["Admin", "Programming", "Security", "Tools"]
tags = ["blockchain", "ethereum", "Parity"]
+++
In <a href="/blockchain-madness/">past article</a> I've talked generally about blockchain technologies, in this article we will look into Ethereum from user perspective. We will build local playground, where we can test many functions of Ethereum(Ethers transfers, using and writing smart contracts and more) without spending real Ethers (and thus real money). This guide in intended for users with Linux OS.<span id="more-1617"></span>


## Setting up Ethereum on my computer


I've explained that Ethereum is distributed peer-to-peer network.   If we join main network any operation in the network costs Ethers, which represent real money.  To play for free we need to join test network, or even better create local development network, which is basically degraded to one node - our client.  Such environment can be very easily set up and yet enable us to try almost all possibilities  of Ethereum network. There are many tutorial how to start with Ethereum client, connect to test network, get some test Ethers and play around. However as Ethereum is developing rapidly, many of them are outdated - so that's also reason why I wrote down my experiences here.

First let's install client - there are many Ethereum clients,  I tried <a href="https://github.com/ethereum/go-ethereum">geth</a> ( written in Go) and <a href="https://parity.io/">parity</a> (written in Rust). I personally found parity more advanced and easier to use then geth (with <a href="https://github.com/ethereum/mist">Mist browser</a>), so I'll continue with parity.


### 1\. Install Parity


On linux it's piece of cake, just run:
`bash <(curl https://get.parity.io -Lk)`

Installation is superfast!


### 2\. Run Parity


Start Parity with following arguments:
`parity --chain dev --tracing=on --fat-db=on --pruning=archive --jsonrpc-cors http://ethereum.github.io`

Argument `--chain dev` starts parity in development mode, with local blockchain, where each transaction is immediately written to blockchain. So it's ideal as our local playground.  Other arguments will be explained later.


### 3\. Open Parity wallet in browser


Open this url in browser: http://127.0.0.1:8180

Go though initial setup wizard to  create your account.


### 4\. Get some Ethers


In order to do anything interesting in our local blockchain we need some Ethers -   it is easy in development mode - in Browser go to `Accounts / Restore` and restore account with empty account recovery phrase.  It restores account with enough Ethers for any tests.


## Playing around


First thing to try is to <strong>send some Ethers</strong> from one account to  another, which is quite straightforward.  In `Accounts tab` select account  and then `Transfer`.  The interesting part of Transfer form is on "advanced sending options",  where we can select maximum amount of <a href="https://ethereum.gitbooks.io/frontier-guide/content/costs.html">gas and gas price</a>, which together determine limit for transaction fee ( amount of gas x gas price).  Also conditions to send transaction in future can be set here.

Each transaction has to be authorized and signed by account owner - see  dialog below:<a href="/wp-content/uploads/signature-screen.png"><img alt="signature-screen" class="alignnone size-full wp-image-1641" decoding="async" height="373" loading="eager" sizes="(max-width: 956px) 100vw, 956px" src="/wp-content/uploads/signature-screen.png" srcset="/wp-content/uploads/signature-screen.png 956w, /wp-content/uploads/signature-screen-300x117.png 300w" width="956"/></a>

After transaction is sent to network, we get transaction hash as it's reference, which is linked to <a href="https://etherscan.io/">etherscan.io</a> blockchain explorer. Unfortunately this does not work in our setup, because etherscan.io is exploring main blockchain (or test networks), but not our private development one.  But we can easily set up local replacement - <a href="https://github.com/gobitfly/etherchain-light">etherchain light </a>\- installation is standard as per instructions, parity client must run with ` -tracing=on --fat-db=on --pruning=archive  `options.  Below is detail of transaction we've sent before (copy link from parity wallet, paste it into etherchain light search box and delete everything before 0x):
<a href="/wp-content/uploads/transaction2.png"><img alt="transaction2" class="alignnone size-large wp-image-1643" decoding="async" height="592" loading="lazy" sizes="(max-width: 884px) 100vw, 884px" src="/wp-content/uploads/transaction2-1024x686.png" srcset="/wp-content/uploads/transaction2-1024x686.png 1024w, /wp-content/uploads/transaction2-300x201.png 300w, /wp-content/uploads/transaction2.png 1147w" width="884"/></a>


###  Wallet is ready to use Smart Contract


As I have explained before Ethereum key feature is Smart Contract - a code that is executed in blockchain. Parity comes with few useful "ready to use" smart contracts.   One of them is <a href="https://github.com/paritytech/parity/wiki/Accounts%2C-Wallets%2C-Vaults">multi-signature wallet</a> \- a contract that stores Ethers for a  group of accounts and several signatures are needed to transfer Ethers from the wallet.  Parity wallet is also good example of potential perils hidden in contracts programming -   just recently implementation of Pahrity wallet had issues which enable unknown hackers to steal 150K Ethers worth $30M.   Such incidents are not so rare in Ethereum (we already mentioned The DAO case in previous article) and show us that complete security is often hard to achieve even for experiences contracts developers. In latest version of Parity wallet contract is already fixed (but it does not fix already deployed contracts, so  wallet users had to move funds from broken wallets).

We can easily try multi-signature wallet ourselves -  add more accounts and follow the directions from link above, we can create for instance wallet with 3 owners, requiring 2 signatures to send money out, if transfer value is above daily limit (which is set during wallet creation).  Also any change to wallet parameters later - like changing daily limit - requires two signatures. We can try few transactions with the new wallet:


<ul>
<li>send some Ethers to wallet - it's same as sending  Ethers between accounts, just select wallet as recipient</li>
<li>sent amount smaller then daily limit from wallet to other account - again it's pretty standard</li>
<li>send amount above the daily limit - now it becomes more interesting - while sending we receive warning that operation has to be approved by other owners.  After we send transaction a request for additional confirmation appears on wallet page as shown below (may need reload page when using dev chain):</li>
</ul>


 

 

<a href="/wp-content/uploads/multiwallet.png"><img alt="multiwallet" class="alignnone wp-image-1653 size-large" decoding="async" height="402" loading="lazy" sizes="(max-width: 884px) 100vw, 884px" src="/wp-content/uploads/multiwallet-1024x466.png" srcset="/wp-content/uploads/multiwallet-1024x466.png 1024w, /wp-content/uploads/multiwallet-300x137.png 300w" width="884"/></a>


<ul>
<li>change daily limit -  two accounts must request exactly same change in order to the change to apply</li>
</ul>




## Developing our first contract


Above we've tried packed contract, now let's try to develop a Smart Contract ourselves.   Smart contracts are developed in language call <a href="https://solidity.readthedocs.io/en/develop/">Solidity</a> (also some other languages exists).  Solidity is language similar to Javascript, but it's typed and compiled to EVM (Ethereum Virtual Machine) bytecode. We start with very simple contract that acts as a global dictionary/hashmap, where everybody can set a string value to given string key (or overwrite existing) and later get the value by querying with yhe key:


```sh
pragma solidity ^ 0.4.0;

contract Dictionary {
    mapping(string=>string) private map;
    
    function set(string key, string value) {
        map[key]=value;
    }
        
    function get(string key) constant returns(string) {
        return map[key];
    }
}
```


Main construct in Solidity is the contract, which is similar to class in OOP - it can contain properties and methods. Contract properties are persisted in Ethereum blockchain. Our contract has just one property, which of type mapping - Solidity built-in hashmap and two method get and set - quite straightforward implementation.  Thanks to it's familiar syntax it easy to start with Solidity programming, but this simplicity can be deceiving - Solidity can have it's quirks, which have fatal security implications (two before mentioned hacks of Ethereum were result of overlooked features of Solidity - recursive calls of contracts and default visibility of methods) - so thorough security review of real contracts is a must.

Now we can deploy our simple contract into dev chain -  in Parity wallet go to `Contracts tab`, click `Develop` and then `New`, paste there the  code and click `Deploy`. Fill contract name and account, which sends contract creation transaction. Click `Next,` confirm transaction with account password and new contract is created - you see its address. Now we can play with the contract  - open it from `Contracts tab` and try to get some values via querying  get method - results are empty strings as we have not store anything in our contract yet. Click Execute and use set function to store some value for some key, verify latter that key contains the value via querying get method again.

Screen for executing method on contract:
<a href="/wp-content/uploads/call_method.png"><img alt="call_method" class="alignnone wp-image-1659 size-large" decoding="async" height="418" loading="lazy" sizes="(max-width: 884px) 100vw, 884px" src="/wp-content/uploads/call_method-1024x484.png" srcset="/wp-content/uploads/call_method-1024x484.png 1024w, /wp-content/uploads/call_method-300x142.png 300w" width="884"/></a>


##  Bit more advanced contract and better development environment


While development environment in Parity is fine for simple contracts,  it's pretty basic (most annoying for me was lack of detailed messages for syntactic errors). But we can easily use other development environment, which is more sophisticated - <a href="http://ethereum.github.io/browser-solidity">Remix</a> \- it is written in Javascript and is available online - just click link before.  Remix has it's own VM (Environment is JavaScript VM), where we can test contracts without any interaction with Ethereum blockchain or we can connect it to our  Parity client (Environment is  Web3 Provider). Remix is connected to Parity via JSON RPC, as Remix is started from online URL, Parity must allow cross site browsing - thats exactly why argument  `--jsonrpc-cors http://ethereum.github.io` is needed on Parity startup.

Our first contract was pretty stupid, now we can try to improve it to something more useful -  a central registry of names. For a small fee users can register any name (string) and assign to it any value(string). Once registered the name cannot be registered or its value changed by  anybody else, but owner can transfer it to other person. Here is contract for our registry:


```sh
pragma solidity ^0.4.0;

contract Registry {
    struct Entry {
        string  value;
        address owner;
    }
    
    mapping(string=>Entry) private map;
    
    uint public fee;
    address registrar;
    
    function Registry(uint initialFee) {
        fee = initialFee;
        registrar = msg.sender;
    }
    
    function register(string key, string value) payable {
        //registration has fee
        require(msg.value >= fee);
        if (map[key].owner == address(0)) {
            // not owned by anybody
            map[key] = Entry(value, msg.sender);
            
        } else {
            // already owned by somebody
            // then only owner can register new value
            require(msg.sender == map[key].owner);
            map[key] = Entry(value, msg.sender);
        }
    }
    
    function transfer(string key, address to) {
        require(map[key].owner == msg.sender);
        string storage value = map[key].value;
        map[key] = Entry(value, to);
    }
    
    function query(string key) constant returns(string) {
        return map[key].value;
    }
    
    function withdraw(uint amount) {
        require(this.balance >= amount && registrar == msg.sender);
        msg.sender.transfer(amount);
    }
}
```


Few things to note here:


<ul>
<li>we define complex type <code>Entry</code> with <code>struct</code> keyword</li>
<li>method <code>Registry</code> (same name as contract) is constructor of the contract - we use it to set amount for registration fee and account that is "registrar", one that created this contract and can use registrations fees.</li>
<li>method <code>register</code> requires that it's called (contract method call is transaction in Ethereum) with some amount of Ethers - representing registration fee - registration is payed service. Ethers are then stored in this contract's balance and only registrar account can transfer them latter to his account with <code>withdraw</code> method
Also note that mapping in Solidity returns default value for non-existent keys (Entry with address 0 and empty string). This is a consequence of how mapping is implemented in EVM.</li>
<li>owner can transfer registered name to other account with <code>transfer</code> method</li>
<li>anybody can <code>query</code> for registered names</li>
</ul>


Now we can play with with contract in Remix - paste the code and click `Publish`, then fill minimum registration fee in box after `Create` button and click `Create` button. Contract is created and we can interact with it's method - register some name (must fill `Value` input with registration fee, strings must be surrounded by double quotes),  query names etc. Also note that methods can be called from different accounts (`Account` select with account address and balance).

Deployed contract in Remix:
<a href="/wp-content/uploads/remix.png"><img alt="remix" class="wp-image-1662 size-full aligncenter" decoding="async" height="932" loading="lazy" sizes="(max-width: 540px) 100vw, 540px" src="/wp-content/uploads/remix.png" srcset="/wp-content/uploads/remix.png 540w, /wp-content/uploads/remix-174x300.png 174w" width="540"/></a>

We can also deploy contract to dev blockchain in running Parity client( or whatever chain is active in the client). Just switch `Environment` to Web3 Provider and `Publish` and `Create` contract again. In Parity wallet authorize contract creation transaction. We can interact with contract here in Remix in a same way as before (but it is new contract) or we can use it in Parity wallet - copy its address (`Copy address` button) and in Parity wallet on `Contracts tab` click `Watch`. Select `Custom Contract` and click `Next`. Paste address, fill name and copy contact interface definition ABI (which is JSON describing available methods), ABI is in `Interface` field in `Contracts Details` in Remix. Finally click `Add Contract`.


## Connect to network


Until now we have been able to work with disconnected Parity client, now it's time to connect it to the test network <a href="https://kovan-testnet.github.io/website/">Kovan</a>, it's still not main blockchain, but we can try interactions that behaves similarly to main network.  We need to stop Parity client and start it again with this command:

`parity --chain kovan`

at the time of my testing Parity had problem with synchronization using quick warp method, if you'll have similar problem you can try:

`parity --chain kovan --no-warp`

Now we have to wait for a while (can be hours in case of slower sync). In meanwhile we can connect to Parity wallet and create accounts (as we are on different blockchain we will have completely new accounts)  . We can also  try to receive some Kovan Ethers, which we'll need for future tests.  Kovan network provides several <a href="https://github.com/kovan-testnet/faucet">faucets</a>, which give you Kovan Ethers for free. Easiest to use is gist based faucet, just create <a href="https://gist.github.com/">gist</a> document with address of your account and run:

`curl http://github-faucet.kovan.network/url --data "address=url_of_your_gist"`

By this method account can receive one Kovan Ether per day.


## Create our own currency


We are going to try one more Smart Contract - <a href="https://github.com/ethereum/EIPs/issues/20">ERC20 Token</a> \-   this is standard for smart contract representing custom currency implemented in Ethereum -  ERC20 Tokens are often used in ICOs and Ethereum wallets have support for such contracts. Luckily Parity has pre-built support for both creation and usage of ERC20 tokens.

Let's start in `Contracts tab` with `Develop`/`Load` and load `Token.sol` from `Snippets`:


```sh
// Abstract contract for the full ERC 20 Token standard
// https://github.com/ethereum/EIPs/issues/20

contract Token {
    /* This is a slight change to the ERC20 base standard.
    function totalSupply() constant returns (uint256 supply);
    is replaced with:
    uint256 public totalSupply;
    This automatically creates a getter function for the totalSupply.
    This is moved to the base contract since public getter functions are not
    currently recognised as an implementation of the matching abstract
    function by the compiler.
    */
    /// total amount of tokens
    uint256 public totalSupply;

    /// @param _owner The address from which the balance will be retrieved
    /// @return The balance
    function balanceOf(address _owner) constant returns (uint256 balance);

    /// @notice send `_value` token to `_to` from `msg.sender`
    /// @param _to The address of the recipient
    /// @param _value The amount of token to be transferred
    /// @return Whether the transfer was successful or not
    function transfer(address _to, uint256 _value) returns (bool success);

    /// @notice send `_value` token to `_to` from `_from` on the condition it is approved by `_from`
    /// @param _from The address of the sender
    /// @param _to The address of the recipient
    /// @param _value The amount of token to be transferred
    /// @return Whether the transfer was successful or not
    function transferFrom(address _from, address _to, uint256 _value) returns (bool success);

    /// @notice `msg.sender` approves `_addr` to spend `_value` tokens
    /// @param _spender The address of the account able to transfer the tokens
    /// @param _value The amount of wei to be approved for transfer
    /// @return Whether the approval was successful or not
    function approve(address _spender, uint256 _value) returns (bool success);

    /// @param _owner The address of the account owning tokens
    /// @param _spender The address of the account able to transfer the tokens
    /// @return Amount of remaining tokens allowed to spent
    function allowance(address _owner, address _spender) constant returns (uint256 remaining);

    event Transfer(address indexed _from, address indexed _to, uint256 _value);
    event Approval(address indexed _owner, address indexed _spender, uint256 _value);
}

```


It defines an interface for ERC20 compliant token. Next we can look at standard implementation `StandardToken.sol`:


```sh
pragma solidity ^ 0.4.0;
/*
You should inherit from StandardToken or, for a token like you would want to
deploy in something like Mist, see HumanStandardToken.sol.
(This implements ONLY the standard functions and NOTHING else.
If you deploy this, you won't have anything useful.)

Implements ERC 20 Token standard: https://github.com/ethereum/EIPs/issues/20
.*/

import "Token.sol";

contract StandardToken is Token {

    function transfer(address _to, uint256 _value) returns (bool success) {
        //Default assumes totalSupply can't be over max (2^256 - 1).
        //If your token leaves out totalSupply and can issue more tokens as time goes on, you need to check if it doesn't wrap.
        //Replace the if with this one instead.
        //if (balances[msg.sender] >= _value && balances[_to] + _value > balances[_to]) {
        if (balances[msg.sender] >= _value && _value > 0) {
            balances[msg.sender] -= _value;
            balances[_to] += _value;
            Transfer(msg.sender, _to, _value);
            return true;
        } else { return false; }
    }

    function transferFrom(address _from, address _to, uint256 _value) returns (bool success) {
        //same as above. Replace this line with the following if you want to protect against wrapping uints.
        //if (balances[_from] >= _value && allowed[_from][msg.sender] >= _value && balances[_to] + _value > balances[_to]) {
        if (balances[_from] >= _value && allowed[_from][msg.sender] >= _value && _value > 0) {
            balances[_to] += _value;
            balances[_from] -= _value;
            allowed[_from][msg.sender] -= _value;
            Transfer(_from, _to, _value);
            return true;
        } else { return false; }
    }

    function balanceOf(address _owner) constant returns (uint256 balance) {
        return balances[_owner];
    }

    function approve(address _spender, uint256 _value) returns (bool success) {
        allowed[msg.sender][_spender] = _value;
        Approval(msg.sender, _spender, _value);
        return true;
    }

    function allowance(address _owner, address _spender) constant returns (uint256 remaining) {
      return allowed[_owner][_spender];
    }

    mapping (address => uint256) balances;
    mapping (address => mapping (address => uint256)) allowed;
}

```


Above is basic implementation of currency -  you can see there use of inheritance (`contract X is Y`)  and events (events are  defined as event constructs and fired within method with particular arguments). We looked at previous two contracts just for reference - to understand how ERC20 token works.  Now we  implement our own token in just few lines of code by inheriting from StandardToken:


```sh
pragma solidity ^0.4.0;

import "StandardToken.sol";

contract MyToken is StandardToken {

    
    // Optional token info
    string public name;                   
    uint8 public decimals;                //How many decimals to show.
    string public symbol;                 

    function MyToken(
        uint256 initialAmount,
        string tokenName,
        uint8 decimalPlaces,
        string tokenSymbol
        ) {
        balances[msg.sender] = initialAmount;
        totalSupply = initialAmount;
        name = tokenName;
        decimals = decimalPlaces;
        symbol = tokenSymbol;
    }
}
```


Create contract above as new contract in Parity (with appropriate arguments) and deploy it.  Once our token contract is deployed we should register it in Token Registry application.  In Parity wallet go to `Applications tab` and start `Token Registry` application. In this application register our new token -  enter token contract address and name, TLA ( 3 letters symbol) and decimals ( these 3 values does not have to be necessarily the same as ones used in token contract creation, as in token contract they are fully optional). Then submit registration  transaction (costs 1 Koven Ether) and new token is registered. Then add  icon to it (with `Add meta-data` button - add there link to image - two transactions are executed - one to register URL (`hintURL`), other to update meta-data (`setMeta`)). Finally our new token registration record may look like below:
<a href="/wp-content/uploads/token.png"><img alt="token" class="size-full wp-image-1676 aligncenter" decoding="async" height="666" loading="lazy" sizes="(max-width: 342px) 100vw, 342px" src="/wp-content/uploads/token.png" srcset="/wp-content/uploads/token.png 342w, /wp-content/uploads/token-154x300.png 154w" width="342"/></a>Once token is registered (with Image) reload Parity wallet in browser and in Accounts you should see our new currency (creating account should have all initial supply of the currency):

<a href="/wp-content/uploads/account.png"><img alt="account" class="size-full wp-image-1679 aligncenter" decoding="async" height="225" loading="lazy" sizes="(max-width: 659px) 100vw, 659px" src="/wp-content/uploads/account.png" srcset="/wp-content/uploads/account.png 659w, /wp-content/uploads/account-300x102.png 300w" width="659"/></a>You can also use new currency in Transfer function (by selecting `type of token transfer`).

\---------

In next article we will look at distributed applications-  DAPPs (we already used one - Token Registry),  which combines contracts and current Web apps (HTML, JS, CSS) into fully functional application than can leverage advantages of the blockchain.
