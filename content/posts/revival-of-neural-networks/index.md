+++
title = "Revival of Neural Networks"
path = "/revival-of-neural-networks/"
date = "2016-08-19T15:27:43"
include_in_feeds = true
[extra]
wordpress_id = 1429
kind = "post"
node_key = "1429"
author = "admin"
source_url = "http://zderadicka.eu/revival-of-neural-networks/"
source_guid = "http://zderadicka.eu/?p=1429"
source_date_gmt = "2016-08-19 14:27:43"
[taxonomies]
category = ["Mathematic", "Programming"]
tag = ["deep learning", "machine learning", "neural networks", "python"]
+++
My actual master studies topic was AI (more then 20 years ago).   Artificial Neural Networks (ANNs) were already known and popular branch of AI and we had some introduction to basics of artificial neural networks (like [perceptron, ](https://en.wikipedia.org/wiki/Perceptron)back propagation, etc.). Though it was  quite interesting topic, I had not seen many practical applications in those days.  Recently  I've chatted with old friend of mine,  who stayed in university and is involved in computer vision research, about recent advancements in AI and computer vision and he told me that most notable change in last years was that neural networks are being now used in large scale. Mainly due to increase in computing power neural networks now can are applied to many real world problems. Another hint about popularity of neural networks came from my former boss, who shared with me this [interesting article](http://www.wired.com/2016/07/artificial-intelligence-setting-internet-huge-clash-europe/) \-  about privacy issues related to machine learning. I've been looking around for a while and it looks like neural networks are becoming quite popular recently - especially architectures with many layers used in so called [deep learning](https://en.wikipedia.org/wiki/Deep_learning). In this article I'd like to share my initial experiences with [TensorFlow](https://www.tensorflow.org/), open source library (created by Google), which can be used to build modern, multi-layered neural networks.<span id="more-1429"></span>

I followed their [advanced tutorial](https://www.tensorflow.org/versions/r0.10/tutorials/mnist/pros/index.html) for handwritten digits recognition (grey picture  28x28 pixels,  [MNIST](http://yann.lecun.com/exdb/mnist/)  dataset of 55 000 pictures) - classical introduction problem in this area .  I implemented it  according to the tutorial (with few modifications, mainly to enable me to play with ANN parameters) in Python3 in [Jupyter](http://jupyter.org/) notebook, which is available [here on gist](https://gist.github.com/izderadicka/d65f904fc5bc4ab5fca3bd4f1e26b6c9).

The architecture of this neural network is on the following picture (It's not exact - just my visualization how it works):

<a href="/wp-content/uploads/neural-net.png"><img alt="neural-net" class="alignnone size-large wp-image-1439" decoding="async" height="416" loading="eager" sizes="(max-width: 884px) 100vw, 884px" src="/wp-content/uploads/neural-net-1024x482.png" srcset="/wp-content/uploads/neural-net-1024x482.png 1024w, /wp-content/uploads/neural-net-300x141.png 300w, /wp-content/uploads/neural-net.png 1452w" width="884"/></a>
**Input layer** is representation of the scanned digit image -  it's 28x28 grey scale picture (normalized to values between 0 - 1).

**First layer** is a [Convolutional layer](https://en.wikipedia.org/wiki/Convolutional_neural_network), in traditional ANN each neuron is connected to every output from previous layer. However in the convolutional layer neuron is connected only to certain window  from previous layer (in our case 5x5 rectangular window).   This window moves through the picture ( by 1 pixel in horizontal or vertical dimensions) and have same parameters for all its positions (thus representing 2D convolution). Convolutional layers are inspired by organization of human visual cortex in our brains and have several advantages. Firstly as the window is local only this layer recognizes and generalizes local features in the image, which can be then used in further processing. Secondly it reduces significantly number of parameters needed to describe the layer, thus allowing to process bigger pictures.
Convolutional layer is combined with Max-Pool layer, which aggregates values from a window (2x2 in our) taking just maximum value within that window for each feature. Window moves by step of 2 pixels - thus resulting data size is reduced by factor of 4 ( by 2 in each dimension) - this is visualized by red pyramids in the picture above.

**Second layer** is also convolutional layer.  It works with 'features' extracted in first layer and thus representing more 'abstract' or 'higher level' features in the image.

**Third layer** is fully connected to previous layer (e.g. more classical ANN layer)  and represents (in my view)  knowledge how to recognize handwritten digits based on local features detected in previous layers. This knowledge is stored in parameters of 1024 neurons in this layer.

**Output layer** has 10 neurons, each representing one digit. The layer is using softmax function, so output can be interpreted as probability distribution function (sum of all outputs is 1). Neuron with highest value represent predicted number and it's output value probability of such result..

This ANN is also using dropout during learning -  about half of neural connections are switched off (weight set to 0) randomly at each learning step. Dropout helps to prevent overfitting (network recognizes perfectly training set, but performs poorly on other data, it's not trained to generalize).

The test according to tutorial code run well -   training of network took more then 1 hour on my notebook (dual core Intel Core i5  @2.7GHz, 16GB memory) and resulting accuracy on test set was 99.22%, which is result advertised in the tutorial.  Mostly misclassified digits were 4, 6 and 9 and on the other hand mostly correctly recognized digits were 1, 3, 2.

I decided to play a bit with this ANN parameters to see how they influence it's accuracy:


<div class="table-scroll" tabindex="0" role="region" aria-label="Reference table"><table>
<tbody>
<tr>
<th>1st Layer size</th>
<th>2nd Layer size</th>
<th>Conv.window size</th>
<th>3rd Layer Size</th>
<th>Accuracy</th>
</tr>
<tr>
<td>32</td>
<td>64</td>
<td>5x5</td>
<td>1024</td>
<td>99.22%</td>
</tr>
<tr>
<td>16</td>
<td>32</td>
<td>5x5</td>
<td>512</td>
<td>99.12%</td>
</tr>
<tr>
<td>64</td>
<td>128</td>
<td>5x5</td>
<td>2048</td>
<td>9.8%</td>
</tr>
<tr>
<td>64</td>
<td>32</td>
<td>5x5</td>
<td>1024</td>
<td>99.12%</td>
</tr>
<tr>
<td>32</td>
<td>64</td>
<td>4x4</td>
<td>1024</td>
<td>99.25%</td>
</tr>
</tbody>
</table></div>


First result is the reference one, based on parameters from tutorial.  If we reduce number of neurons to half in all 3 hidden layers, accuracy drops just by 0.1%.   Same if we switch sizes of first and second convolutional layers. Some results look contra-intuitive at first look - if we double size of all 3 hidden layers, suddenly networks is performing very poorly - accuracy 9.8% - actually network recognizes correctly just zeros (one would expect that more neurons will make network 'smarter'). Possible explanation is that now network is just too big for given training data set - it does not contain enough information for network to learn (I also tried to increase size of one learning step from 50 to 200 samples, but it did not help). We can identify this problem even during learning stage, where we can see that accuracy is not improving during learning - in previous cases, accuracy quickly increased to over 90%, in this case it stays around 10% for all learning steps.

By reducing convolution window size to 4x4 we can achieve even slightly better results ( by 0.03%) then recommended parameters from tutorial.

Experiments with this network confirmed to me what I already remember about neural networks - they can be fairly tricky -  without in depth knowledge it's hard to set optimal parameters and frequently network does not learn as expected.  My friend from university confirmed me that often it's kind of 'black magic' to design right neural network for given problem.

Also interpreting knowledge hidden in a neural network and understanding why networks provided particular result can be fairly complex task or even not possible at all.  Consider following picture, which shows 9s misclassified by our network (configured with the last set of parameters and achieving 99.25% accuracy):
<a href="/wp-content/uploads/nines.png"><img alt="nines" class="alignnone size-full wp-image-1444" decoding="async" height="543" loading="lazy" sizes="(max-width: 700px) 100vw, 700px" src="/wp-content/uploads/nines.png" srcset="/wp-content/uploads/nines.png 700w, /wp-content/uploads/nines-300x233.png 300w" width="700"/></a>

Clearly we as humans would match some of these 9 correctly (first row second and third) and it's hard to argue why our network decided otherwise.


## Conclusions


Neural networks have seen huge renaissance in past few years.  Neural networks are now being used in production in many areas (image recognition/classification - Facebook passes billions of images daily to it's ANNs , speech recognition - Google uses ANN for it's Voice services , data classification ...)  and are able to achieve better results that traditional machine learning algorithms. Main progress here can be contributed to advancement in hardware performance,  but also to new neural network techniques, especially focused on effective learning.  Neural networks with many hidden layers (deep networks) are now technically possible.

In this article I've played with one of available neural network libraries TensorFlow according to it's instructional tutorial. Even this tutorial small was very  enlightening and showed me the  progress in this area. However key issues of neural networks, as I remember them from past, still remains to some extent -  problematic/complex choice of network layouts and parameters and difficult task of how to interpret knowledge stored in the network (or understand why network behaves in particular way).

But for sure current neural networks libraries provide many possibilities and there are many opportunities how to explore them. I'll try to learn bit more and leverage them in some future projects.
