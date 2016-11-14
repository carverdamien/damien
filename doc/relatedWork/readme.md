# Related Work
todo: define the work scope
## Userspace
## Virtualization
* Autoballooning
* PUMA
## Lightweight Virtualization
### Container Manager
### Linux Kernel Control Groups
* Jonathan Corbet July 31, 2007 [Controlling memory use in containers](http://lwn.net/Articles/243795/) : There is, thus, a significant cost associated with the memory controller - the addition of five pointers (one in struct page, four in struct meta_page) and one atomic_t for every active page in the system can only hurt.
* Balbir Singh and Vaidyanathan Srinivasan, 2007  [Containers: Challenges with the memory resource controller and its performance](https://www.kernel.org/doc/ols/2007/ols2007v2-pages-209-222.pdf)
* Kamezawa hiroyu Nov 19, 2008 [Cgroup And Memory Resource Controller](https://www.linuxfoundation.jp/jp_uploads/seminar20081119/CgroupMemcgMaster.pdf)
* Kamezawa hiroyuki Jun 29, 2008 [Memory controller soft limit introduction](https://lkml.org/lkml/2008/6/29/253)
* Kamezawa hiroyu Oct 22, 2009 [Memory Resource Controller](https://events.linuxfoundation.org/images/stories/slides/jls09/jls09_kamezawa.pdf)
* Johannes Weiner Nov 11, 2011 [mm: memcg: remove optimization of keeping the root_mem_cgroup LRU lists empty](https://lkml.org/lkml/2011/11/8/414): The global per-zone LRU lists are about to go away on memcg-enabled kernels, with all pages being exclusively linked to their respective per-memcg LRU lists.
* Christoph Hellwig Jun 7, 2011 [mm: make per-memcg lru lists exclusive](https://lkml.org/lkml/2011/6/7/184)
* Some Blog Aug 15, 2013 [All About the Linux Kernel: Cgroup’s Redesign](https://www.linux.com/blog/all-about-linux-kernel-cgroups-redesign): Cgroup allows fine-grained resource partitioning among competing processes running on the same machine.
