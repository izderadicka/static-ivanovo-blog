+++
title = "Performance Should Matter"
path = "/performance-should-matter/"
date = "2020-02-15T10:49:36"
include_in_feeds = true
[extra]
wordpress_id = 2154
kind = "post"
node_key = "2154"
author = "admin"
source_url = "http://zderadicka.eu/performance-should-matter/"
source_guid = "http://zderadicka.eu/?p=2154"
source_date_gmt = "2020-02-15 09:49:36"
[taxonomies]
category = ["Programming"]
tag = ["Coding exercises", "Rust"]
+++
As I did not have much time to focus on larger programming projects recently I've done several exercises on [exercism](https://exercism.io) Rust track. It was quite fun and I hope learned a bit. But I found one issue there - when looking at solutions of others, some of them, even when code look very nice and has stars from other users, is performing very badly. I consider this as quite bad practice - if one chooses a "Systems Programming Language" as Rust he should think about performance and understand implications  of: 






a) **general algorithm complexity**<br/>So chosen solution should try to use sound algorithm, with complexity close to best possible






b) **using complex fancy functional constructs**<br/>Rust is advertising "zero cost abstractions", however while it works in many cases it has to be used with caution - you have to use a bit of common sense.




<span id="more-2154"></span>




So now for couple of  use case:






### Prime Factorization






All times classic - prime factorization - find all prime factors of the number. Here is my rather conservative solution:






```rust
pub fn factors(mut n: u64) -> Vec<u64> {
    let mut factors = vec![];
    while n % 2 == 0 {
        factors.push(2);
        n /= 2;
    }
    let mut d = 3;
    while d * d <= n {
        if n % d == 0 {
            factors.push(d);
            n /= d;
        } else {
            d += 2;
        }
    }
    if n > 1 {
        factors.push(n);
    }
    factors
}
```






And here is most up voted solution from exercism (praised for simplify and understandable code):






```rust
 pub fn factors(mut n: u64) -> Vec<u64> {
    let mut factors = Vec::new();
    let mut candidates = 2..;

    while n > 1 {
        let x = candidates.next().unwrap();

        while n % x == 0 {
            n /= x;
            factors.push(x);
        }
    }

    factors
}
```






And now look at performance (using cargo bench for factorization of number 93\_819\_012\_551), `bench_mine` is first code example, `bench_other` second:






```
running 2 tests
 test bench_mine  … bench:      29,628 ns/iter (+/- 12,447)
 test bench_other … bench:   5,285,123 ns/iter (+/- 445,111)
```






So first code is about 180x faster then other. Why is that? Key insight is that we can test only to square root of n ( because for larger number we have already tested other smaller dividend). And indeed we do not need to test even numbers - we know they are not primes.






### Crypto Square






This is simple exercise on simple cryptographic algorithm - you organize text into approximately square matrix and then you read it by columns, rather then by rows ( e.g. transpose matrix). Here is my reference "Keep It Simple Stupid" implementation:






```rust
 pub fn encrypt(input: &str) -> String {
    let text: Vec<char> = input
        .chars()
        .filter(|c| !c.is_ascii_whitespace() && !c.is_ascii_punctuation())
        .map(|c| c.to_ascii_lowercase())
        .collect();

    let sz = text.len();
    let r = (sz as f64).sqrt() as usize;
    let c = if r * r == sz { r } else { r + 1 };
    let mut cipher = String::with_capacity(r * c + r);
    for col in 0..c {
        for row in 0..r {
            let pos = row * c + col;
            cipher.push(if pos < sz { text[row * c + col] } else { ' ' })
        }
        if col != c - 1 {
            cipher.push(' ')
        }
    }
    cipher
}

```






It's nothing fancy, first lines just remove spaces and punctuation from text, then calculates matrix dimensions (to be square or number of rows and columns differs max by 1). 






Then there are two cycle - going through matrix first by columns rather the by rows and separating each columns by space (so code look like something you'd create in C/C++ - nothing fancy just good old procedural code (apart of spaces cleaning)).






Now compare with following code (which got some appreciation and stars from exercism community)  - it's utilizing many of functional features of rust - closures, higher order functions etc.:






```rust
pub fn encrypt(input: &str) -> String {
    let chars = || {
        input
            .chars()
            .flat_map(|c| c.to_lowercase())
            .filter(|c| c.is_alphanumeric())
    };
    let len = chars().count();
    let (rows, cols) = match (0..).find(|n| n * n >= len).unwrap() {
        0 => return String::new(),
        n if n * (n - 1) >= len => (n, n - 1),
        n => (n, n),
    };

    let square_row = |row| {
        let mut col = chars().skip(row).step_by(rows);
        (0..cols).map(move |_| col.next().unwrap_or(' '))
    };

    (1..rows).fold(square_row(0).collect(), |mut out, row| {
        out.push(' ');
        out.extend(square_row(row));
        out
    })
}
```






Looks nice - right? But now let's measure performance (using cargo bench - for random text of 10\_000 characters - `bench_mine` is my reference implementation, `bench_other` is later functional implementation:






```
running 2 tests
test bench_mine  … bench:      74,181 ns/iter (+/- 53,961)
test bench_other … bench:  33,410,235 ns/iter (+/- 18,083,158)
```






So it does make a difference in performance, doesn't it? First solution is just about 330 times faster. So what if we try it for 100\_000 characters:






```
running 2 tests
test bench_mine  … bench:     764,747 ns/iter (+/- 275,125)
test bench_other … bench: 1,185,014,036 ns/iter (+/- 880,062,279)
```






Now the difference is even bigger -  first is 1500 x faster. So why it that? Later code is functional, all right, but Rust promises "zero costs abstractions", so it should be compiled to efficient code automagically? But actually in this case it cannot be "zero cost "- `skip` and `step_by` are not equivalent (from performance perspective) to direct indexing of vector - former still needs to call `next` for each intermediate entry - so time complexity is `O(x)` vs `O(1)` \- using iterators here adds on complexity here (but it does not have to be the case in other use cases) - so instead of `O(n)` it's something like `O(n^2)`, which indeed makes difference for larger input sizes.






## Rail Fence Cipher






Here the performance difference is not huge (spoiler only 5x), but I think it's good example of "small" but obvious impacts on performance. 






The Rail Fence cipher is a form of transposition cipher that gets its name from
the way in which it's encoded. It was already used by the ancient Greeks.






In the Rail Fence cipher, the message is written downwards on successive "rails" of an imaginary fence, then moving up when we get to the bottom (like a zig-zag). Finally the message is then read off in rows.






Here is my implementation:






```rust
pub struct RailFence {
    rails: usize,
}

struct RailIter {
    sz: usize,
    pos: usize,
    intervals: [usize; 2],
    interval_index: usize,
    interval_step: usize,
}

impl RailIter {
    fn new(rails: usize, rail_no: usize, sz: usize) -> Self {
        let period = 2 * rails - 2;
        let interval1 = period - 2 * rail_no;
        let interval2 = period - interval1;
        let (interval_index, interval_step) = match (interval1, interval2) {
            (0, 0) => unreachable!("At least one interval is non-zero"),
            (0, _) => (1, 0),
            (_, 0) => (0, 0),
            (_, _) => (0, 1),
        };
        RailIter {
            sz,
            pos: rail_no,
            intervals: [interval1, interval2],
            interval_index,
            interval_step,
        }
    }
}

impl Iterator for RailIter {
    type Item = usize;
    fn next(&mut self) -> Option<Self::Item> {
        if self.pos < self.sz {
            let res = self.pos;
            let interval = self.intervals[self.interval_index];
            self.interval_index = (self.interval_index + self.interval_step) % 2;
            self.pos += interval;
            Some(res)
        } else {
            None
        }
    }
}

impl RailFence {
    pub fn new(rails: u32) -> RailFence {
        assert!(rails > 0);
        RailFence {
            rails: rails as usize,
        }
    }
    pub fn encode(&self, text: &str) -> String {
        let text: Vec<_> = text.chars().collect();
        let sz = text.len();
        (0..self.rails)
            .flat_map(|i| RailIter::new(self.rails, i, sz))
            .map(|pos| text[pos])
            .collect()
    }

    pub fn decode(&self, cipher: &str) -> String {
        let cipher: Vec<_> = cipher.chars().collect();
        let sz = cipher.len();
        let mut res = vec![' '; sz];

        (0..self.rails)
            .flat_map(|i| RailIter::new(self.rails, i, sz))
            .enumerate()
            .for_each(|(cipher_pos, cleartext_pos)| res[cleartext_pos] = cipher[cipher_pos]);
        res.iter().collect()
    }
}
```






Key is `RailIter` iterator, which return indexes according to cipher algorithm, probably not smartest implementation, but works.  Then `encode` and `decode` is rather simple. And here for comparison is nice  small mostly functional solution, which received most votes:






```rust
pub struct RailFence {
    rails: usize
}

impl RailFence {
    pub fn new(rails: u32) -> RailFence {
        RailFence { rails: rails as usize }
    }

    pub fn encode(&self, text: &str) -> String {
        let mut result = vec![Vec::new(); self.rails];
        for (c, i) in text.chars().zip(zigzag(self.rails)) {
            result[i].push(c);
        }
        result.iter().flat_map(|c| c).collect::<String>()
    }

    pub fn decode(&self, cipher: &str) -> String {
        let mut indexes : Vec<_> = zigzag(self.rails).zip(1..).take(cipher.len()).collect();
        indexes.sort();

        let mut char_with_index : Vec<_> = cipher.chars().zip(indexes).map(|(c, (_, i))| (i, c)).collect();
        char_with_index.sort();
        char_with_index.iter().map(|(_, c)| c).collect()
    }
}

fn zigzag(n: usize) -> impl Iterator<Item = usize> {
    (0..n - 1).chain((1..n).rev()).cycle()
}
```






And now runtime comparison for encoding and decoding (and comparing result to original message) for random string of 1M length:






```
test mine  … bench:  11,246,027 ns/iter (+/- 832,466)
test other … bench:  67,304,512 ns/iter (+/- 6,375,399)
```






So first and obvious performance drawback is use of sort in decode - sort is of O(n.log(n)) complexity, while other solution complexity is linear, so it's important to realize that sort is not for free. Plus I think there is one more allocation in `decode`, not sure how much it impacts performance. For true details about performance one should try some profiling.






## Conclusion






I've presented couple of  cases where niceness of code was preferred over performance and I hope I've explained my point - if doing coding exercises, one should always look for efficient solution - meaning solution that is performing well. That should be true for all languages, but as Rust is a "system programing language" it's even more important here - why then to choose such language, if my code is clumsy and hurting performance significantly?






Some programing learning/evaluation platforms (like [codility](https://app.codility.com/programmers/), which is quite explicit on complexity tests, or [HackerRank](https://www.hackerrank.com), which contains test cases for large input data sets, which timeouts for inefficient solution)  do take this in account and apart of functional test, they also measure that solution is performing within expected limits. That's is great because it forces you to come up with sound solution. <br/>(Unfortunately codility does not support Rust language and HackerRank only partially)
