+++
title = "From Russia with Love - Kotlin Language"
path = "/from-russia-with-love-kotlin-language/"
date = "2018-03-26T07:07:13"
include_in_feeds = true
[extra]
wordpress_id = 1841
kind = "post"
node_key = "1841"
author = "admin"
source_url = "http://zderadicka.eu/from-russia-with-love-kotlin-language/"
source_guid = "http://zderadicka.eu/?p=1841"
source_date_gmt = "2018-03-26 06:07:13"
categories = ["Programming"]
tags = ["Kotlin"]
+++
One may think that we have already more then enough programming languages. But community thinks differently and new languages keeps popping up and thanks for that, because some  bring cool innovative features, others focus on more streamlined and effective development, but all of them contribute to the evolution of the IT industry. Because as in the nature progress comes through the variety of species and competition between them.  As I have written in<a href="/in-rust-we-trust/"> my past article</a> I looked recently into Rust language - very interesting language, which comes with novel approach to memory management without garbage collection, but still assuring high security of the program.  Nowadays I met another member of ever-growing happy family of programing languages - Kotlin and I'd like to share my first experiences in this article.<span id="more-1841"></span><span id="more-1841"></span>

Kotlin language was engineered in JetBrains - a global leader in IDEs and similar developer tools. Though company is incorporated here in Czech Republic, most of its brainpower is from Russia (so for the title). Name of the language is taken from Kotlin (Ко́тлин) island in the beautiful city of the St.Petersburg.  In some presentation Jetbrain guys said that they were inspired by Java taking it's name from an island in Indonesia ( which I think is a misconception - because Java language name  is taken from the other meaning of the word - coffee - so more proper name in this sense would be Espresso or Cappuccino).

Actually Kotlin is not so recent language, the development started in 2010 about same time as <a href="https://swift.org/">Swift</a>, however it experienced a major boom in popularity recently just about a year ago when Google announced it's official support for Android.  Recent <a href="https://insights.stackoverflow.com/survey/2018#most-loved-dreaded-and-wanted">2018 Stackoverflow survey</a> shows that Kolin made it to number 2 in 'most loved' languages (just after the Rust).

Authors present their language as "pragmatic" - not focusing very much on innovation, but more on developers productivity and convenience. Kotlin is achieving this by building on Java and extending it with many popular language features found in other languages like Python, Scala, Haskel, Rust, JavaScript etc. In this approach it's similar to above mentioned Swift, to which it's often compared.  Popular features in Kotlin are centered around functional programing - lambda functions, higher order functions (which feel more natural here then in Java 8, functions are true first order citizens ) and improved type system with null type safety and type inference. These features alone can help a lot, but Kotlin add many other goodies - more concise syntax, delegation support, possibility to extend existing classes with extension functions to name few notable.

Just to give you a taste of Kotlin, let's use one of my favorites Kotlin features - extension function:


```sh
fun String.capitalizeWords(): String {
    val words = split(' ')
    return words.map{
        it[0].toUpperCase() + it.substring(1)
    }.joinToString(" ")
}

fun main(args: Array<String>) {
	println("sedm lumpu slohlo pumpu".capitalizeWords())
}
```


Above we define function `capitalizeWords`, which turns first letter of each word to upper case. This function then can be used on every string.

Key Kotlin strength is 100% compatibility with JVM and Java in both directions: not only you can easily use all existing Java libraries, but also you can use Kotlin code in Java code almost with same ease. And this is strong selling point,  language is not only about it's syntax, but also very much about core and contributed libraries (which can be seen in other great languages like OCAML, where it's a bit of problem and limit it's acceptance). And here Kotlin can profit from extensive and mature Java ecosystem.

Another big advantage of Kotlin is excellent IDE - as being developed by JetBrains it has first class support in IDEA and Android Studio with all the goodies of advanced IDE - completion, code search, refactoring etc.

I'm using Kotlin currently for Android development (which is kind of gloomy endeavour, but this is for another article), where I started from scratch with Kotlin.   It's fairly easy to learn Kotlin, if you have some Java basics (or similar language like C#). Basics of Kotlin can learned in few days and more advanced usage comes painlessly  later. Language feels quite friendly and one can easily write code in very natural way.  Especially for me, who has been working with mostly Python and recently with Rust, Kotlin syntax feels very convenient and much easier to follow then Java. When learning Kotlin, I found this book very useful - <a href="https://www.manning.com/books/kotlin-in-action">Kotlin in Action by Dmitry Jemerov; Svetlana Isakova from Manning Publications</a> \- it's well written, quickly guides you through key language features, can be read in few days and after that you are ready to start with Kotlin in real project.

Concerning performance: compilation performance looks good, similar to Java (see detailed comparison <a href="https://www.manning.com/books/kotlin-in-action">here</a>). Runtime performance is advertised to be same as Java, however Kotlin requires small runtime library to support all of it's features. I guess there might be some small runtime overhead in some cases (see for instance this <a href="https://sites.google.com/a/athaydes.com/renato-athaydes/posts/kotlinshiddencosts-benchmarks">benchmark</a>), but it does not seem to be significant - actually in some cases Kotlin can improve performance because it's library contains more standard functions, which can replace custom suboptimal code in many cases.

So generally my first impressions from Kotlin are quite positive, language is nice, easy to start with (also thanks to its IDE), many features that I used in other languages are now available here, definitely simplifies Android development.
