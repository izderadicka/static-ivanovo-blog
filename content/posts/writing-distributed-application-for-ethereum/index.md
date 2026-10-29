+++
title = "Writing Distributed Application for Ethereum"
path = "/writing-distributed-application-for-ethereum/"
date = "2017-09-04T08:05:49"
include_in_feeds = true
[extra]
wordpress_id = 1685
kind = "post"
node_key = "1685"
author = "admin"
source_url = "http://zderadicka.eu/writing-distributed-application-for-ethereum/"
source_guid = "http://zderadicka.eu/?p=1685"
source_date_gmt = "2017-09-04 07:05:49"
categories = ["Programming"]
tags = ["Aurelia", "ethereum", "Parity"]
+++
In <a href="/ethereum-local-playground/">past article</a> I've written about some basic stuff we can do with <a href="https://www.ethereum.org/">Ethereum</a> client <a href="https://parity.io/">Parity</a> \- like transfering Ethers, creating multi-signature wallet and even writing our own contracts. Now I'll continue with writing our very own Distributed Application ( Dapp).<span id="more-1685"></span>


## What is Dapp?


In my understanding Distributed Application  is combination of contract(s) deployed in Ethereum blockchain and browser based UI that enables easy interaction with contracts. Some of application logic that is  normally hosted in server,  is in Smart Contracts in the distributed system - Ethereum - so that why they are called distributed. System is shown on following picture:
<a href="/wp-content/uploads/dapp-schema.jpg"><img alt="dapp-schema" class="alignnone size-full wp-image-1688" decoding="async" height="1137" loading="eager" sizes="(max-width: 800px) 100vw, 800px" src="/wp-content/uploads/dapp-schema.jpg" srcset="/wp-content/uploads/dapp-schema.jpg 800w, /wp-content/uploads/dapp-schema-211x300.jpg 211w, /wp-content/uploads/dapp-schema-720x1024.jpg 720w" width="800"/></a>

So Dapp consists of two parts - browser client, written in Javasript and Smart Contract(s), written in Solidity (or other Ethereum language). Browser calls contract(s) via <a href="http://www.jsonrpc.org/specification">JSON-RPC </a> (interface is <a href="https://github.com/ethereum/wiki/wiki/JSON-RPC">standardized</a> across Ethereum browsers, so Dapp browser part can theoretically work with any client). Though we can call directly JSON-RPC methods from general JavaScript, it's much easier to use existing library <a href="https://github.com/ethereum/web3.js/">web3.js</a>, which provides convenient objects and methods.


## Our Dapp - Name Registry


For our demo Dapp we use contract from previous article, but improved slightly by adding event to notify about new name registration:


```sh
pragma solidity ^0.4.0;

contract Registry {
    struct Entry {
        string  value;
        address owner;
    }
    
    event Register(string name, address who);
    
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
            Register(key, msg.sender);
            
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


For UI part we  use Aurelia (as I have <a href="/starting-with-aurelia-pagination-with-back-and-sort/">played with Aurelia</a> framework before, so this is good opportunity to refresh  knowledge), <a href="https://getbootstrap.com/docs/3.3/">Bootstrap 3</a>  and web3.js for communication with Ethereum client. The resulting code is <a href="https://github.com/izderadicka/dapp-demo-registry">here in github</a>.

When creating this simple Dapp following two things showed as tricky:


<ul>
<li>Web application packing -  as several times before correct packing of web application was problematic. Finally web3.js worked correctly with <a href="https://webpack.js.org/">webpack</a> bundled application generated with Aurelia CLI and using recent version (3.5) of webpack.</li>
<li>Web3.js version -  initially I started with latest beta version (1.0), but it does not seem to be ready yet, documentation is brief and I was missing some functionality or it was not working properly, so I finally used stable version 0.20.  This is a pity, because 1.0.0 has much modern interface, using Promises etc.</li>
</ul>


The core ES6 class for interaction with `Registry` contract is `client.js`:


```javascript
import Web3 from 'web3';


// needs to be changed to address of actual contract
const contractAddress ='0x2CdB6AE9F7B24fb636b95d9060ff0D0F20e836D6';
const contractABI = [{"constant":false,"inputs":[{"name":"amount","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"key","type":"string"},{"name":"value","type":"string"}],"name":"register","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"key","type":"string"}],"name":"query","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"fee","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"key","type":"string"},{"name":"to","type":"address"}],"name":"transfer","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"initialFee","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"name":"name","type":"string"},{"indexed":false,"name":"who","type":"address"}],"name":"Register","type":"event"}];

function toPromise(fn, ...args) {
    return new Promise((resolve, reject) => {
        if (! (typeof(fn) === 'function')) {
            reject("Param is not a function");
        } else {
        try {
        fn(...args, (err,v) => {
            if (err) {
                reject(err)
            } else {
                resolve(v);
            }
        })
        }
        catch(e) {
            reject("Function call error: "+ JSON.stringify(e));
        }
    }
    })
}

export class Client {
    constructor() {
        this.fee = 0;
        let web3;
        if (typeof web3 !== 'undefined') {
            web3 = new Web3(web3.currentProvider);
        }
        else if (window.location.pathname == "/register/") {
            // in parity
            let rpcURL = `${window.location.protocol}//${window.location.host}/rpc/`;
            web3 = new Web3(new Web3.providers.HttpProvider(rpcURL));
          } else {
            // set the provider you want from Web3.providers
            web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
          }
        this.web3 = web3;
        window.web3 = web3; // just for development

        
        this.registry = this.web3.eth.contract(contractABI).at(contractAddress);
        
        toPromise(this.registry.fee.call)
        .catch(e => console.log(`Fee error: ${JSON.stringify(e)}`))
        .then(v =>{
                this.fee = v;
                console.log(`Fee is ${this.fee}`);
                }
        );

        this._listeners = [];
        let fromBlock = this.web3.eth.blockNumber-10000;
        this.registry.Register({},{fromBlock, toBlock:'latest'}).watch((err,data) => {
            if (!err) {
                console.log(`Got event ${JSON.stringify(data)}`)
                setTimeout(() => {
                    for (let l of this._listeners) {
                        l(data);
                    }
                }, 0)
            }
        });

        this._listeners = [];
    }

    addListener(fn) {
        this._listeners.push(fn);
    }

    get connected() {
        let now = new Date();
        if (! this._last || (now -this._last) > 10000) {
            this._last = now; 
            this._conn = this.web3.isConnected();
            return this._conn;
        } else {
            return this._conn;
        }
    }

    query(name) {
        return toPromise(this.registry.query.call,name);
    }

    register(name, value) {
        let address = this.web3.eth.accounts[0];
        // fist estimate gas in local VM
        let data = this.registry.register.getData(name, value);
        let estimatePromise = toPromise(this.web3.eth.estimateGas,
            {
             to: this.registry.address,
             data:data,   
            from: address,
            value: this.fee});
        //then send it to blockchain
        let sendPromise = estimatePromise
            .then( (gas) => { 
            console.log(`Estimate succeded with ${gas}`);
            return toPromise(this.registry.register.sendTransaction, name, value,
            {from: address,
            value: this.fee,
            gas
            })
        });
        // and get reciept
        let receiptPromise = sendPromise.then(txHash => {
            let txSendTime = new Date()
            return new Promise((resolve, reject)=> {
                let checkReceipt = () => {
                this.web3.eth.getTransactionReceipt(txHash,
                    (err,r) =>{
                        if (err) {
                            reject(err)
                        } else if (r && r.blockNumber) {
                            resolve(r)
                        } else if (new Date() - txSendTime > 60000) {
                            reject(new Error(`Cannot get receipt for 60 secs, check manually for ${txHash}`));
                        } else {
                            window.setTimeout(checkReceipt, 1000);
                        }
                    });
                };
                checkReceipt();
            });
        });
        
        return {send: sendPromise, receipt: receiptPromise, estimate: estimatePromise};
    }

    
    
}
```


Client must know address of the contract  (`contractAddress`) and its interface (`contractABI`).  As I do prefer to work with promises rather then callbacks, there is an utility function `toPromise` that converts callback to promise.

Two functions, important for user interface, are `query`, which queries the registry, and `register`, which registers new name. Of these two later is more interesting  - the interaction with blockchain is done in 3 steps:


<ol>
<li>Call is evaluated locally with <code>web3.eth.estimateGas</code> -  it executes contract method in local EVM.  More important then knowing consumed gas is the fact that call executes without problems.  If we do not check this now, we can easily send transactions that will fail ( for instance trying to register already registered name), but even such transactions are sent out and included in blockchain. This early check prevents such problems.</li>
<li>Send out signed transaction - this step requires cooperation of Parity wallet, were transaction has to be signed.</li>
<li>Get notification that transaction was included in the blockchain. Method <code>web3.eth.getTransactionReceipt</code> can return null, if there are not enough new blocks confirming our transaction ( to be reasonably sure that transaction is not in the orphaned block), so we have to try several times until receipt is available.</li>
</ol>


Method `addListener` enables to listen to `Register` events and update application about recently registered names.

Apart of the code above rest of the application is usual Aurelia UI stuff.   Finally application looks like this:
<a href="/wp-content/uploads/dapp1.png"><img alt="dapp1" class="alignnone size-large wp-image-1691" decoding="async" height="283" loading="lazy" sizes="(max-width: 884px) 100vw, 884px" src="/wp-content/uploads/dapp1-1024x328.png" srcset="/wp-content/uploads/dapp1-1024x328.png 1024w, /wp-content/uploads/dapp1-300x96.png 300w" width="884"/></a>

And here is screen for querying registry:
<a href="/wp-content/uploads/dapp2.png"><img alt="dapp2" class="alignnone size-large wp-image-1692" decoding="async" height="300" loading="lazy" sizes="(max-width: 884px) 100vw, 884px" src="/wp-content/uploads/dapp2-1024x348.png" srcset="/wp-content/uploads/dapp2-1024x348.png 1024w, /wp-content/uploads/dapp2-300x102.png 300w" width="884"/></a>


## Other tutorials


You can check for instance this <a href="https://github.com/paritytech/parity/wiki/Dapp-Tutorial">Parity Dapp tutorial</a> \- which is focused particularly on Parity's special libraries integrating with <a href="https://facebook.github.io/react/">React</a>. I went through it (with some issues, partly related again to web application packaging) and it's really nice. Parity libraries provides cool reactive components - like `TransactButton` button, which visualizes transactions steps. Such components can significantly speed up and simplify application development.


## Conclusion


We only scratched surface of distributed applications development, real applications are indeed much more complex, with numerous cooperating contracts in blockchain, dynamically created contracts etc.  But it's first step and it's not very difficult - web part is basically regular web app development with one additional library - web3.js and few gotchas - especially around sending transactions out.  Smarts contracts language Solidity is also relatively easy to comprehend, but as we've shown in previous articles it can be deceiving and one can make fatal errors, which make distributed application vulnerable. Security review of contracts based of solid understanding of Ethereum blockchain is a must for real applications.
