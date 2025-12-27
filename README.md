# 🧠 Thread-Safe LRU Cache (with TTL, Metrics & RWLock)

A **high-performance, thread-safe LRU (Least Recently Used) Cache** implemented from scratch in Python using core data structures and concurrency primitives.  
Designed to mimic **real-world caching systems** (e.g., Redis / in-memory caches) with strong emphasis on **correctness, performance, and extensibility**.

---

## ✨ Features

- **O(1) `get` and `put` operations**
- **Thread-safe** using a **Read–Write Lock (RWLock)**
- **Per-key TTL (Time-To-Live)** for automatic expiry
- **Cache metrics** (hit count, miss count, hit ratio)
- **Pluggable eviction strategy** (Strategy Pattern)
- Custom **Doubly Linked List** (no library shortcuts)
- Clean, extensible, interview-ready design

---

## 📌 Why this project?

Most cache implementations stop at a basic LRU.  
This project goes further by addressing **real production concerns**:

- Concurrent access in multi-threaded environments
- Read-heavy workload optimization
- Entry expiration (TTL)
- Observability via metrics
- Separation of eviction policy from cache mechanics

This makes the project **far more than a DSA exercise**.

---

## 🏗️ High-Level Design

### Core Data Structures

| Component | Purpose |
|---------|--------|
| HashMap (`dict`) | O(1) key → node lookup |
| Doubly Linked List | Maintain access order (MRU → LRU) |
| RWLock | Allow concurrent reads, exclusive writes |
| Strategy Pattern | Decouple eviction policy |

---

## 🧩 Architecture Diagram

                 ┌───────────────────────────┐
                 │        HashMap (dict)      │
                 │   key  ──►  Node reference │
                 └──────────────┬────────────┘
                                │
                                ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │  HEAD    │◄──►│   MRU   │◄──►│   ...   │◄──►│   LRU   │◄──►│  TAIL   │
    │ (dummy)  │    │ (recent)│    │         │    │ (oldest)│    │ (dummy) │
    └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘

    Doubly Linked List (Access Order)



- **HEAD** and **TAIL** are dummy nodes
- Recently accessed items move closer to **HEAD**
- Eviction happens at **TAIL.prev**

---

## 🔁 Cache Flow

### `get(key)`
1. Acquire **read lock**
2. Lookup key in hashmap
3. If expired → upgrade to write lock, remove entry
4. Otherwise → upgrade to write lock, move node to MRU
5. Update metrics and return value

### `put(key, value)`
1. Acquire **write lock**
2. Update existing entry OR insert new entry
3. If capacity exceeded → evict using eviction strategy
4. Insert new node at MRU position

---

## 🔐 Concurrency Model (RWLock)

### Why Read–Write Lock?

Typical caches are **read-heavy**.

| Lock Type | Behavior |
|---------|---------|
| Mutex | Only one reader or writer ❌ |
| RWLock | Multiple readers, exclusive writers ✅ |

This implementation allows:
- **Concurrent reads**
- **Safe writes and structural updates**

---

## ⏱️ TTL (Time-To-Live)

Each cache entry can expire independently.

- TTL stored **per node**
- Checked lazily on `get`
- Expired entries are removed automatically

This mirrors real cache behavior in production systems.

---

## 📊 Metrics & Observability

The cache tracks:
- Total hits
- Total misses
- Hit ratio

```python
cache.stats()

```
### Example Output

```json
{
  "hits": 42,
  "misses": 18,
  "hit_ratio": 0.7
}
```
# 🧠 Cache System Design

## Eviction Strategy (Strategy Pattern)

The eviction logic is decoupled from the core cache mechanics using the **Strategy Pattern**. This ensures a clean separation of concerns and allows for high extensibility.

### Eviction Strategy Interface
```python
class EvictionStrategy:
    def select_node_for_eviction(self, cache):
        raise NotImplementedError
```

### Default Strategy: LRU Eviction
```python
class LRUStrategy(EvictionStrategy):
    def select_node_for_eviction(self, cache):
        # The least recently used node is always located at tail.prev, allowing O(1) eviction.
        return cache.tail.prev
```

### Why This Matters
* **Separation of Concerns:** Clean separation between **policy** (what to evict) and **mechanism** (how the cache storage works).
* **Extensibility:** New strategies (FIFO, LFU) can be added without modifying the core cache internals.
* **Technical Signal:** Demonstrates a strong understanding of system design principles (Open/Closed Principle) in technical interviews.

---

## ⏳ Time & Space Complexity

### Time Complexity
| Operation | Complexity | Note |
| :--- | :--- | :--- |
| **get** | $O(1)$ | Hashmap lookup and node repositioning. |
| **put** | $O(1)$ | Hashmap insertion and head update. |
| **eviction** | $O(1)$ | Strategy-based selection is constant time. |

### Space Complexity
* **$O(\text{capacity})$**: Storage scales linearly with the defined capacity for both the hashmap and the doubly linked list.

---

## 🚀 Example Usage

```python
# Initialize cache with capacity=2 and TTL=3 seconds
cache = LRUCache(capacity=2, ttl=3)

cache.put(1, "A")
cache.put(2, "B")

cache.get(1)       # returns "A"

# Wait for TTL to expire
time.sleep(4)
cache.get(1)       # returns -1 (expired)

# Test eviction
cache.put(3, "C")  # capacity reached, evicts key=2 (least recently used)
cache.get(2)       # returns -1

cache.stats()
```

---

## 🧪 Testing Notes

The cache is designed to be safe under concurrent access and correctly handles:
* **Capacity overflow:** Automated eviction logic.
* **Expired entries:** Lazy cleanup based on TTL.
* **Key Updates:** Smooth handling of repeated updates to the same key.
* **Thread Safety:** Concurrent reads and writes managed via `RWLock`.

**Possible Testing Extensions:**
* Multithreaded stress tests.
* Performance benchmarks for latency tracking.
* Custom eviction strategy validation.

---

## 📌 Possible Extensions (Optional)

* **LFU (Least Frequently Used):** An eviction strategy based on access counts.
* **Proactive Cleanup:** A background thread to remove expired entries instead of lazy deletion.
* **Per-key TTL:** Override the global TTL for specific high-priority keys.
* **Distributed Wrapper:** Wrap the implementation for use in a distributed environment (e.g., Redis-like behavior).
* **Backend Integration:** Integration into an API caching layer.
