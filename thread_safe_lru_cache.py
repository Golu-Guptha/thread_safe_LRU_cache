import threading
import time
import math


class RWLock:
    def __init__(self):
        self.readers = 0
        self.readers_lock = threading.Lock()
        self.writer_lock = threading.Lock()

    def acquire_read(self):
        with self.readers_lock:
            self.readers += 1
            if self.readers == 1:
                self.writer_lock.acquire()

    def release_read(self):
        with self.readers_lock:
            self.readers -= 1
            if self.readers == 0:
                self.writer_lock.release()

    def acquire_write(self):
        self.writer_lock.acquire()

    def release_write(self):
        self.writer_lock.release()


class Node:
    def __init__(self, key, value, ttl=None):
        self.key = key
        self.value = value
        self.expiry = time.time() + ttl if ttl else None
        self.prev = None
        self.next = None


class EvictionStrategy:
    def select_node_for_eviction(self, cache):
        raise NotImplementedError


class LRUStrategy(EvictionStrategy):
    def select_node_for_eviction(self, cache):
        return cache.tail.prev


class LRUCache:
    def __init__(self, capacity, ttl=None, eviction_strategy=None):
        self.capacity = capacity
        self.ttl = ttl
        self.cache = {}

        self.hits = 0
        self.misses = 0

        self.eviction_strategy = eviction_strategy or LRUStrategy()
        self.rwlock = RWLock()

        self.head = Node(0, 0)
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node

    def print_cache(self):
        curr = self.head.next
        while curr != self.tail:
            print(f"{curr.key}:{curr.value}, ttl of {curr.value}={math.floor(curr.expiry - time.time()) if curr.expiry else None}")
            curr = curr.next
            

    def _insert_at_front(self, node):
        first = self.head.next
        self.head.next = node
        node.prev = self.head
        node.next = first
        first.prev = node

    def _is_expired(self, node):
        return node.expiry is not None and time.time() > node.expiry

    def get(self, key):
        self.rwlock.acquire_read()
        try:
            if key not in self.cache:
                self.misses += 1
                return -1

            node = self.cache[key]

            if self._is_expired(node):
                self.rwlock.release_read()
                self.rwlock.acquire_write()
                try:
                    self._remove(node)
                    del self.cache[key]
                    self.misses += 1
                    return -1
                finally:
                    self.rwlock.release_write()

            self.rwlock.release_read()
            self.rwlock.acquire_write()
            try:
                self._remove(node)
                self._insert_at_front(node)
                self.hits += 1
                return node.value
            finally:
                self.rwlock.release_write()

        finally:
            pass

    def put(self, key, value):
        self.rwlock.acquire_write()
        try:
            if key in self.cache:
                node = self.cache[key]
                node.value = value
                node.expiry = time.time() + self.ttl if self.ttl else None
                self._remove(node)
                self._insert_at_front(node)
                return

            if len(self.cache) >= self.capacity:
                node_to_evict = self.eviction_strategy.select_node_for_eviction(self)
                self._remove(node_to_evict)
                del self.cache[node_to_evict.key]

            new_node = Node(key, value, self.ttl)
            self.cache[key] = new_node
            self._insert_at_front(new_node)

        finally:
            self.rwlock.release_write()

    def stats(self):
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": self.hits / total if total else 0.0
        }


if __name__ == "__main__":
    cache = LRUCache(capacity=2, ttl=3)
    try:
        cache.put(1, "A")
        cache.put(2, "B")
        cache.print_cache()
        print(cache.get(1))
        time.sleep(4)
        if(cache.get(1) == -1):
            print("Key 1 has expired")
        if (cache.get(2) == -1):
            print("Key 2 has expired")  

        cache.put(3, "C")
        
        print(cache.get(3))
        cache.print_cache()
        print(cache.stats())
    except Exception as e:
        print(f"An error occurred: {e}")
