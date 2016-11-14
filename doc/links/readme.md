# Links
* Jonathan Corbet July 31, 2007 [Controlling memory use in containers](http://lwn.net/Articles/243795/) : There is, thus, a significant cost associated with the memory controller - the addition of five pointers (one in struct page, four in struct meta_page) and one atomic_t for every active page in the system can only hurt.

* Balbir Singh and Vaidyanathan Srinivasan, 2007  [Containers: Challenges with the memory resource controller and its performance](https://www.kernel.org/doc/ols/2007/ols2007v2-pages-209-222.pdf)