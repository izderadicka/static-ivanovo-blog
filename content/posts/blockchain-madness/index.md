+++
title = "Blockchain madness"
path = "/blockchain-madness/"
date = "2017-08-16T09:43:02"
include_in_feeds = true
[extra]
wordpress_id = 1666
kind = "post"
node_key = "1666"
author = "admin"
source_url = "http://zderadicka.eu/blockchain-madness/"
source_guid = "http://zderadicka.eu/?p=1666"
source_date_gmt = "2017-08-16 08:43:02"
[taxonomies]
category = ["Security", "Technology"]
tag = ["blockchain", "ethereum"]
+++
Some technologies I really notice only when they hit me directly into the face.   That's the case of [blockchain](https://en.wikipedia.org/wiki/Blockchain)  -  I have been looking into [Bitcoin](https://en.wikipedia.org/wiki/Bitcoin) several years back and found it quite interesting (especially from cryptographic perspective - as interesting usecase for applied cryptography), but never expected that it'll reach such extensive grow in popularity as we have seen in past half year or so.   This forced me to looked again into these technologies and get bit more detailed understanding about blockchain technologies, why it's so popular now and particularly look at recent development and on  next big player in this area [Ethereum](https://www.ethereum.org/) project.

In this article I'll share some initial thoughts of mine about blockchain, what I think it is and why it matters. In later article(s) we'll look into  Ethereum from purely practical perspective. We will build a local playground for Ethereum, where we can try immediately some basic functions of the system.<span id="more-1666"></span>


## So what is the  "blockchain"?


For me blockchain is unification of three core concepts which work closely together:



- **peer-to-peer network** of open source clients
- **append-only public database** (blockchain in its specific meaning of the word) that stores  "messages" from the peer-to-peer network and is organized as blocks of records,where recent block seals previous blocks and assures their integrity. Blocks are replicated across clients.
- **consensus protocol** that enables clients to store "messages" in blockchain database in a consistent manner - e.g. in a way where majority of clients  agrees that stored messages are "valid" and also agrees on the order in which they are stored in the blockchain DB.



<a href="/wp-content/uploads/blockchain2.png"><img alt="blockchain2" class="alignnone size-full wp-image-1623" decoding="async" height="591" loading="eager" sizes="(max-width: 523px) 100vw, 523px" src="/wp-content/uploads/blockchain2.png" srcset="/wp-content/uploads/blockchain2.png 523w, /wp-content/uploads/blockchain2-265x300.png 265w" width="523"/></a>

While the implementation with trusted (by all clients) central entity, which maintains the master blockchain database, is relatively simple, the key value of current blockchain technologies is  that systems are  **decentralized**, with no central trusted entity and they can work properly even if a minority of peer-to-peer clients (weighed by their contribution to consensus, not necessary by pure numbers)  is malicious and they are trying to actively misuse the system. To achieve the decentralization and resilience to such attacks blockchain  systems are based on modern **cryptography**.

While components of the blockchain existed before Bitcoin, only in Bitcoin they have been ingeniously glued together by mysterious [Satoshi Nakamoto](https://en.wikipedia.org/wiki/Satoshi_Nakamoto) and it was Bitcoin that started era of blockchain systems as we see them now.  After Bitcoin we have seen myriads of similar projects, some were almost identical to Bitcoin (cloning Bitcoin and changing few parameters) , some were inventive and discovered new possibilities in blockchain technologies. Ethereum is one of such systems, going beyond original scope of Bitcoin to provide a digital currency and creating trusted decentralized computing platform.  Ethereum can execute code pieces called [ Smart Contracts](https://en.wikipedia.org/wiki/Smart_contract) on clients in peer-to-peer network and this code maintains shared state of the systems maintained in blockchain. With Smarts Contracts one can implements things like new digital currencies, trusted voting systems, gambling systems, [predictions markets](https://en.wikipedia.org/wiki/Prediction_market), central registries, [blind auctions](https://en.wikipedia.org/wiki/First-price_sealed-bid_auction) and much more.  Theoretically anything can be done, because Ethereum Smarts Contracts are [Turing complete](https://en.wikipedia.org/wiki/Turing_completeness).


## Why to care about blockchain?


I think there are two main reasons why blockchain is interesting - financial and technical - so let's look at then in more details.


### Financial aspect


Cryptocurrencies and blockchain technologies attracted attention of financial investors in past years and now there  is significant amount of money circulating in the cryptocurencies - right now at the time of writing of this article market capitalization of top 10 cryptocurencies is about $75 billions (. app. 1/10 of Apple, which is company with biggest market cap).  Speculative trading with cryptocurencies becomes more and more populars and we hear many stories about people who made a fortune on cryptocurencies trading (if you invested $1000 in Ether on Jan 1st 2016, cryptocurency of Ethereum, your investment would be worth now approximately $24k, but because cryptocurrencies market is very volatile you may as well loose your money in future).

Frantic speculative investments is not the only aspect of financial activities around blockchain.  We can see also numerous new companies that appear out of nowhere promising to create innovative solutions based on blockchain technologies.  And surprisingly easily such companies found financing worth  millions of $,  usually through cryptocurrency offerings - so called [ICOs (Initial Coin Offerings)](http://www.investopedia.com/terms/i/initial-coin-offering-ico.asp),  where company creates new cryptocurrency (which is now extremely easy in Ethereum), selling that currency to public, promising some king of participation on future success of the company.  To start such ICO it's enough to have website and some "whitepaper" about using blockchain or improving blockchain.  Many of such "companies" already proved as scum,  others even if they have good ideas and honest intent will struggle in future to execute that.  One satirical example of current situation around ICOs is this website [Useless Ethereum Token](https://uetoken.com/), which is ICO that plainly announced that all money send to it will be use only for someone's personal benefits and sender will receive nothing in return. Yet it seems some people send money (Ethers) to it and currency (UET) [is traded](https://coinmarketcap.com/assets/useless-ethereum-token/#charts) on some exchanges (I do not believe that guy made $65k he claimes, if you look [into blockchain](https://etherscan.io/address/0x27f706edde3aD952EF647Dd67E24e38CD0803DD6), only $4.6k worth of ether came into the contract, but still interesting that something that proclaims itself as completely useless is gaining a value).

The situation now around blockchain and cryptocurrencies reminds me[ dot-com bubble](https://en.wikipedia.org/wiki/Dot-com_bubble) from mileanium end.  Then also a lot of speculative money went into technological companies based on unrealistic expectations of their future profits. It's my personal opinion that many cryptocurrencies and blockchain companies are speculatively overestimated and we might see collapse in future,  probably even worth then dot-com one, because cryptocurrencies markets and ICOs are basically not regulated at all.


### Technological aspect


Apart of financial frenzy around blockchain technological aspect is surely interesting.   Technology is relatively new and it's not clear yet what will be it's implications.  Ethereum project is speaking about Web 3.0 as new revolution in web technologies, serverless  applications communicating with peer-to-peer blockchain  network  that maintains applications logic  and state (but this is only one of competing visions for next 'version' of the web) .  My current feeling is that blockchain technologies are slightly over-hyped, probably due to their financial aspect.  From popular articles it  may look that all future computing will be running in blockchain ( like for instance this discussion about [implementing neural networks and deep learning in blockchain](https://www.reddit.com/r/MachineLearning/comments/4bhmqb/decentralized_deep_learning_on_a_blockchain_ai/)).  Blockchain surely brings some interesting possibilities for distributed computing, especially possibility to have distributed  database/ledger, which is consistent by consensus and updated in decentralized ways.   However this comes at costs of massive replication and redundant efforts - in Ethereum for instance each computation must be done on every node in the peer-to-peer nerwork and system status is replicated  on each node too - which basically means inherited inefficiency and  performance limitations. For certain type of applications it's desirable compromise to leverage other unique features of blockchain, but for other applications, which require intensive computation and processing of huge amount of  data (like above mentioned neural networks and deep learning) it's limiting.

One of key  assets of blockchain technology is possibility to replace trusted central authority with decentralized solution, which assures similar level of security and safeguards.  So majority of blockchain based projects is about to replace this or that central authority (central bank, stock exchange, logistic company, lottery organizer, etc.), promising that system will work much better without central trusted entity.  While it might be good solution in many cases I believe it's not an universal solution.  Often it's easier and more efficient to trust certain central authority, which has good incentives to keep system running and behave properly. Trusted central authority can also help  with arbitrations, in cases where technology fails (look for instance at [The DAO hack](https://coinmarketcap.com/currencies/ethereum-classic/), when Ethereum  project initiated hard fork of the blockchain (splitting system into two "independent" ones - Ethereum and Ethereum Classic) to refund $50M of stolen Ethers and thus bypassing the key foundation principle  of the Ethereum - immutability of the blockchain).

But enough of theoretical talk, the best way how to understand some technology is to play with it and that's what we will do in the next article.
