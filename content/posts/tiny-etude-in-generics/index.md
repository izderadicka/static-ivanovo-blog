+++
title = "Tiny Etude in Generics"
path = "/tiny-etude-in-generics/"
date = "2018-10-04T15:24:19"
include_in_feeds = true
[extra]
wordpress_id = 1933
kind = "post"
node_key = "1933"
author = "admin"
source_url = "http://zderadicka.eu/tiny-etude-in-generics/"
source_guid = "http://zderadicka.eu/?p=1933"
source_date_gmt = "2018-10-04 14:24:19"
categories = ["Programming"]
tags = ["Generics", "Rust"]
+++
Although Rust is mostly noted for it's memory safety and thus most prominent feature is borrow checker, it has also very decent type system, which was inspired by modern functional languages like OCAML or Haskel. In this article I'll look into very simple example, which will however show some nice features of Rust type system - especially generics.<span id="more-1933"></span>

So problem is very simple -  create a product of an vector of values (in Rust it would be a slice type, which is more general) in most generic way, so it can be used on broadest possible range of value types ( the problem is of course solve in standard library, but this is meant as a small exercise).

So let's start with first attempt - we know for sure that our generic type needs to implement `Mul` trait (to multiply values) :


```rust
fn product<T>(vals: &[T])-> T
 where T: std::ops::Mul
    
 {
     assert!(vals.len()>0);
     let mut res = vals[0];
     for x in &vals[1..] {
         res = res * (*x);
     }
     
     res
 }
```


As often with first attempts in Rust this one even does not compile. There are two issues here:


<ul>
<li>Result of multiplication is associated type of <code>Mul</code> trait, but we are returning type <code>T</code> - we have to be explicit here and link <code>T</code> to <code>Mul Output</code></li>
<li>we cannot just move or deference values out of the slice.  <code>T</code> has to be <code>Copy</code> for this code to work.</li>
</ul>


So fixed version looks like this:


```rust
fn product<T>(vals: &[T])-> T
 where T: std::ops::Mul<Output=T>+Copy
    
 {
     assert!(vals.len()>0);
     let mut res = vals[0];
     for x in &vals[1..] {
         res = res * (*x);
     }
     
     res
 }
```


So now it works for all `Copy` types, but it's still restrictive - we can make it easily work with all `Clone` types (which is superset of `Copy` types):


```rust
fn product<'a, T>(vals: &'a[T])-> T
 where T: std::ops::Mul<Output=T> + Clone,
    
 {
     assert!(vals.len()>0);
     let mut res = vals[0].clone();
     for x in &vals[1..] {
         res = res * x.clone();
     }
     
     res
 }
```


However this approach is a bit inefficient, because we need to clone every value. If we look how `Mul` is implemented for standard numeric types, we see that right hand side could be also a reference to value (&T). This looks promising , as we will not need to clone in the loop. The only other quirk is that lifetime for &T has to be explicit here - &'a T:


```rust
fn product<'a, T>(vals: &'a[T])-> T
 where T: std::ops::Mul<&'a T,Output=T> + Clone,
    
 {
     assert!(vals.len()>0);
     let mut res = vals[0].clone();
     for x in &vals[1..] {
         res = res * x;
     }
     
     res
 }
```


Now we can replace loop with more elegant iterator:


```rust
fn product<'a, T>(vals: &'a[T])-> T
 where T: std::ops::Mul<&'a T,Output=T> + Clone,
    
 {
     assert!(vals.len()>0);
     vals[1..].iter().fold(vals[0].clone(), |acc,x| acc*x) 
 }

```


Now question is if we can get rid of `Clone` dependency?  Actually we do not need first value of the slice, we can start with multiplicative identity - e.g. 1.   Crate `num` provides this concept:


```rust
extern crate num;
use num::One;
  
fn product<'a, T>(vals: &'a[T])-> T
 where T: std::ops::Mul<&'a T,Output=T> + One,
    
 {
     assert!(vals.len()>0);
     vals.iter().fold(T::one(), |x,y| x*y)
     
 }
```


It looks nice and clean, but there is one practical problem -  `One` is not implemented for floating point types (because of quirks of binary FP calculations in real computer).

So finally we can take a look how things are properly implemented in standard library. Iterator trait provides this method:


```rust
fn product<P>(self) -> P
        where Self: Sized,
              P: Product<Self::Item>,
    {
        Product::product(self)
    }
```


So it's works for all types that implements trait `Product`:


```rust
pub trait Product<A = Self> {
    fn product<I>(iter: I) -> Self
    where
        I: Iterator<Item = A>;
}
```


And `Product` trait is implemented for all numerical types (including floating point values) for both value and reference iterators.

So our function could use it as:


```rust
use std::iter::Product;
fn product<'a, T>(vals: &'a[T])-> T
 where T: Product<&'a T>,
    
 {
     assert!(vals.len()>0);
     vals.iter().product()
 }

```


 


## Conclusions


Rust type system is quite powerful, which can be seen even in such simple example as is product of vector of values.
