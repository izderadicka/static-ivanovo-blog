+++
title = "Decoding Audio Captchas in Python"
path = "/decoding-audio-captchas-in-python/"
date = "2014-08-24T12:11:14"
include_in_feeds = true
[extra]
wordpress_id = 834
kind = "post"
node_key = "834"
author = "admin"
source_url = "http://zderadicka.eu/decoding-audio-captchas-in-python/"
source_guid = "http://zderadicka.eu/?p=834"
source_date_gmt = "2014-08-24 11:11:14"
categories = ["Programming", "Security"]
tags = ["captcha", "python", "speech recognition"]
+++
For good or bad many sites are now using CAPTCHAs to determine if visitor is human or computer program. Captcha presents a task - usually reading some distorted letters  and writing them back to a form.  This is considered to be hard for computer to do, so user must be human.  To improve accessibility visual captchas are accompanied by audio captchas, where letters are spelled (usually with some background noise to make letters recognition more difficult) .  However audio captchas are know to be easier to break.  Inspired by <a href="http://www.captcha.net/Breaking_Audio_CAPTCHAs.pdf">this article</a> \[1\]  I created a python implementation of audio captchas decoding using commonly available libraries and with just a general knowledge of speech recognition  technologies. Software is called <a href="https://github.com/izderadicka/adecaptcha">adecaptcha</a> and I tested it on couple of sites, where I got 99.5% accuracy of decoded letters for one site and 90% accuracy for other site (which has much distorted audio).<span id="more-834"></span>


### General approach


We can divide task of recognizing spelled letters into 3 separate sub-tasks, each one is using  a bit different technologies and approach:


<ol>
<li><strong>Signal segmentation</strong>
We start with continuous sound signal, where we have several spoken letters and between them there is a silence or background noise.  We have to cut signal into parts that contain just one spoken letter.</li>
<li><strong>Features extractions</strong>
We have to represent each sound with set of features, which characterize well each letter sound and which is not too big.  We get so call features vector - a set of numbers, that we can use later for classification.</li>
<li><strong>Classification</strong>
To feature vectors calculated from a letter sounds we have to assign correct letter - all sounds for same letter form  same class - thus we use term classification.
Classification usually has two steps:
Learning: Based on manually classified training set (feature vector + correct letter), our classification  algorithm learns how to classify  arbitrary feature vector. Result of learning is the model.
Classification:  Using previously created model we can now classify unknown feature vectors into classes - e.g. recognize spoken letters.</li>
</ol>




### Test data


Initially we will use captchas from site uloz.to -   here is one sample captcha:
<a href="/wp-content/uploads/captcha.gif"><img alt="captcha" class="alignnone size-full wp-image-845" decoding="async" height="70" loading="eager" src="/wp-content/uploads/captcha.gif" width="175"/></a>

and here is corresponding sound:



<audio controls="" preload="metadata"><source src="/wp-content/uploads/captcha.wav" type="audio/wav"/></audio>



We usually get data as PCM signal (or if it is .mp3 we can easily decode with <a href="http://spacepants.org/src/pymad/">pymad</a>)

So our signal looks like this (sample rate 16kHz):
<a href="/wp-content/uploads/pcm_data_with_time_axes.png"><img alt="pcm_data_with_time_axes" class="alignnone size-full wp-image-848" decoding="async" height="1052" loading="lazy" sizes="(max-width: 1938px) 100vw, 1938px" src="/wp-content/uploads/pcm_data_with_time_axes.png" srcset="/wp-content/uploads/pcm_data_with_time_axes.png 1938w, /wp-content/uploads/pcm_data_with_time_axes-300x162.png 300w, /wp-content/uploads/pcm_data_with_time_axes-1024x555.png 1024w" width="1938"/></a>

As you can see there are 4 areas with high volume of sound - these are spoken letters and there is a noise between them. We can move now to our first task, segmentation:


### Segmentation


Segmentation is a critical task - all future success depends on fact that we are able to identify areas, where spoken letter is in the signal.  There are many sophisticated techniques used in speech recognition, with advanced options how to mitigate disruptive effects of the noise.  However not being and expert I used something simple - just calculated mean energy (square of amplitude) over a small rectangular window (<a href="http://www.numpy.org/">numpy</a> function `convolve` is very useful for this). On picture below you can see this 'energy envelope' of the signal and planned segmentation of the signal:

<a href="/wp-content/uploads/segmented.png"><img alt="segmented" class="alignnone size-full wp-image-849" decoding="async" height="1052" loading="lazy" sizes="(max-width: 1938px) 100vw, 1938px" src="/wp-content/uploads/segmented.png" srcset="/wp-content/uploads/segmented.png 1938w, /wp-content/uploads/segmented-300x162.png 300w, /wp-content/uploads/segmented-1024x555.png 1024w" width="1938"/></a>

We use a threshold value (green horizontal line) to find segments of sound.  Anything above it is letter sound, which ends, when signal is below threshold for at least 0.1 sec. We also add a small amount of time before and after letter segment, so we get better capture of start and end of the sound.  Letter sound segments are marked with vertical lines - red is start, yellow end of segment. With separated letter sounds we can start features extraction.


### Features extraction


In speech recognition technologies <a href="http://en.wikipedia.org/wiki/Mel-frequency_cepstrum">MFCCs (Mel-frequency cepstral coefficients)</a> are used to get features for letter or syllable sound. MFCC is basically a spectrum of frequency spectrum (applying twice time domain to frequency domain transformation) and it is believed to be good characterization of  some sound, invariant to certain extent to background noise or to speaker pronunciation.

We use very straightforward implementation, based  <a href="http://en.wikipedia.org/wiki/Mel-frequency_cepstrum">Wikipedia article</a>:


<ol>
<li>We make the <a href="http://en.wikipedia.org/wiki/Fourier_transform" title="Fourier transform">Fourier transform</a> of letter sound. Below you can see frequency spectrum for two letters X and B:
<a href="/wp-content/uploads/spectrum_letter_X_and_B.png"><img alt="spectrum_letter_X_and_B" class="alignnone size-full wp-image-850" decoding="async" height="1052" loading="lazy" sizes="(max-width: 1938px) 100vw, 1938px" src="/wp-content/uploads/spectrum_letter_X_and_B.png" srcset="/wp-content/uploads/spectrum_letter_X_and_B.png 1938w, /wp-content/uploads/spectrum_letter_X_and_B-300x162.png 300w, /wp-content/uploads/spectrum_letter_X_and_B-1024x555.png 1024w" width="1938"/></a>
As you can see frequency characteristics of each letter are different - B having higher lower frequencies, X having significant higher frequencies (over 5kHz) - representing 'hissing' in the letter sound.</li>
<li>Map the powers of the spectrum obtained above onto the <a href="http://en.wikipedia.org/wiki/Mel_scale" title="Mel scale">mel scale</a>, using <a href="http://en.wikipedia.org/wiki/Window_function#Triangular_window" title="Window function">triangular overlapping windows</a>.
We would like to represent spectrum only with selected frequencies -  this reflect human psychoacoustics model, which tells us that we are not able to recognize two distinctive sounds if they have similar frequencies. We hear just one sound (the stronger one). This is called masking effect (and it's used also in audio compression).   Also our perception of sound pitch(frequency) is not linear -  for lower frequencies we are able to recognize it more precisely,  while for higher frequencies the interval between two sounds, which we perceived having different frequency, is much bigger. This is what mel scale is about - mel scale maps frequencies to a scale that is linear according to our perception.
So we can have smaller distance between frequencies on lower frequency, and bigger on higher frequencies and still keep most of information perceived by human .
Following picture shows our filter bank (each filter is triangular window):
<a href="/wp-content/uploads/mel_filters.png"><img alt="mel_filters" class="alignnone size-full wp-image-853" decoding="async" height="1052" loading="lazy" sizes="(max-width: 1938px) 100vw, 1938px" src="/wp-content/uploads/mel_filters.png" srcset="/wp-content/uploads/mel_filters.png 1938w, /wp-content/uploads/mel_filters-300x162.png 300w, /wp-content/uploads/mel_filters-1024x555.png 1024w" width="1938"/></a>
Each triangle represents  a filter  for frequency at triangle top. Triangles are overlapping as requested and you can clearly see how their base is getting bigger with increasing frequency (to reflect the mel scale).</li>
<li>Take the <a href="http://en.wikipedia.org/wiki/Logarithm" title="Logarithm">log</a> of the powers at each of the mel frequencies.
Below is picture of filtered power spectrum from previous step - in log vertical scale:
<a href="/wp-content/uploads/power_spectrum_letter_b_and_x.png"><img alt="power_spectrum_letter_b_and_x" class="alignnone size-full wp-image-855" decoding="async" height="1052" loading="lazy" sizes="(max-width: 1938px) 100vw, 1938px" src="/wp-content/uploads/power_spectrum_letter_b_and_x.png" srcset="/wp-content/uploads/power_spectrum_letter_b_and_x.png 1938w, /wp-content/uploads/power_spectrum_letter_b_and_x-300x162.png 300w, /wp-content/uploads/power_spectrum_letter_b_and_x-1024x555.png 1024w" width="1938"/></a>
You can again see spectrum characteristics of X and B letters we've spoken before.</li>
<li>Take the <a href="http://en.wikipedia.org/wiki/Discrete_cosine_transform" title="Discrete cosine transform">discrete cosine transform</a> of the list of mel log powers, as if they were a signal.
DCT transformation is available in <a href="http://www.scipy.org/">scipy</a> package in scipy.fftpack.dct</li>
<li>The MFCCs are the amplitudes of the resulting spectrum.
And finally here we have MFCCs for our two letters:
<a href="/wp-content/uploads/mfccs_letter_b_and_x.png"><img alt="mfccs_letter_b_and_x" class="alignnone size-full wp-image-856" decoding="async" height="1052" loading="lazy" sizes="(max-width: 1938px) 100vw, 1938px" src="/wp-content/uploads/mfccs_letter_b_and_x.png" srcset="/wp-content/uploads/mfccs_letter_b_and_x.png 1938w, /wp-content/uploads/mfccs_letter_b_and_x-300x162.png 300w, /wp-content/uploads/mfccs_letter_b_and_x-1024x555.png 1024w" width="1938"/></a></li>
</ol>


Now we have feature vector with 40 numbers and can use it for classification.


### Classification


For classification we use <a href="http://en.wikipedia.org/wiki/Support_vector_machine">SVM</a> algorithm.  There are several reasons for choosing it:


<ul>
<li>According to literature [1], SVM provides good results in this area</li>
<li>Nice open source implementation exists - <a href="http://www.csie.ntu.edu.tw/~cjlin/libsvm/">libsvm</a></li>
<li>libsvm has binding for python</li>
<li>It's very easy to create model for libsvm, package contains script <code>tools/easy.py</code>, which  basically does all work for you.</li>
</ul>


For targeted site we got 500 captchas, which represent 2000 letters -  1800 were used for training. 200 were control set, to test accuracy of classification for created model (which was 99.5%). For preparation of training set we used `samplestool.py` from <a href="https://github.com/izderadicka/adecaptcha">adecaptcha</a> package, which helps to manually classify samples (shows captcha picture, plays sound, does segmentation, saves transcribed letters, generates training set). All task of preparing training data took bit more then one hour (most time consuming is manually transcribing training captchas).

Detailed procedure for generating model is in adecaptcha <a href="http://bazaar.launchpad.net/~ivan-zderadicka/adecaptcha/trunk/view/head:/README">README file</a>.


### Other captchas


The approach above was initially applied to uloz.to captchas,  which are relatively clear, with minimum background noise. But what about site where captchas are more distorted - like these:



<audio controls="" preload="metadata"><source src="/wp-content/uploads/sample97.wav" type="audio/wav"/></audio>




<audio controls="" preload="metadata"><source src="/wp-content/uploads/sample98.wav" type="audio/wav"/></audio>



It turned out that we can still get  90% accuracy of individual letters (here letters are digits) recognition, which for 4 letters captchas provides app. 65% accuracy of recognizing captcha correctly. It helped here that segmentation was relatively easy and fixed segments could be used.


### Conclusion


Usually it's easier to decode audio captcha then visual one.  Technology for this is available and can be used by relative laymen in area of speech recognition like myself.

Implementation in python is provided in package <a href="https://github.com/izderadicka/adecaptcha">adecaptcha</a>, which works quite well for test site (uloz.to) with almost 100% accuracy and it takes app. 0.3 sec to decode audio captcha -   so it can be easily used in practice. Even for more noisy captchas we can achieve 65% accuracy in recognized captchas, which is still fairly practical ( only 4% of attempts need more then 3 tries).

Possible improvements:


<ul>
<li>Better segmentation -  reliable segmentation is the key, it could be improved to be more noise tolerant and more generic (parameters must be fine tuned for each set of samples to work reliably)</li>
<li>MFCC implementation is the basic one -   there are many improvement, which can make it better for this particular domain - recognition of spelled letters/digits</li>
</ul>




### References


\[1\] Jennifer Tam,Jiri Sima,Sean Hyde, Louis von Ahn: <a href="http://www.captcha.net/Breaking_Audio_CAPTCHAs.pdf">Breaking Audio CHAPTCHAs</a>
