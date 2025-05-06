# Assorted

1. Web + iOS + Android + Backend for a photo album
    1. Create an album
    2. Upload images to the album
    3. Convert images to webp formats:
        1. Normal version: width at most 1920px and height at most 1080px; aspect ratio unchanged.
        2. Thumbnail version: width and height at most 512px, aspect ratio 1:1, scaled and center-cropped vertically and horizontally.
        3. Store the images persistently.
    4. View album's image thumbnails and enlarged version when clicked
    5. Delete a single image in an album
    6. Delete an album
2. LeetCode
    1. https://leetcode.com/problems/find-common-characters/description/
    2. https://leetcode.com/problems/count-the-number-of-good-nodes/description/
    3. https://leetcode.com/problems/first-missing-positive/description/

# Notes
1. Languages
    1. Programming languages: C/C++/JavaScript/TypeScript/Python3/Go/Swift/Kotlin
    2. Natural languages: English
2. Album
    1. Please provide README.md with instructions to run locally
    2. Docker compose is recommended
3. LeetCode
    1. Only code snippets are required
    2. The snippets must be accepted by LeetCode
4. System
    1. macOS or Linux
5. Quality expectation
    1. Everything can be examined, make sure you tried your best. No need to rush.
6. Getting started
    1. Make a fork of this repository and start coding now!.


## 專案展示

- [Album-Android 影片展示](https://youtube.com/shorts/qKNCqSaeQis)
- [Album-iOS 影片展示](https://youtube.com/shorts/Avmr8ThnCos)

---

## LeetCode 題解

### LeetCode 1

```python

class Solution:
    def commonChars(self, words: List[str]) -> List[str]:
        common = {}
        
        for w in words[0]:
            if w in common:
                common[w] += 1
            else:
                common[w] = 1
        
        for word in words[1:]:
            for k, v in common.items():
                n = word.count(k)
                if n > 0:
                    common[k] = min(v, n)
                else:
                    common[k] = 0

        result = []
        for k, v in common.items():
            if v > 0:
                result.extend(k * v)

        return result




```

---

### LeetCode 2

```python
from collections import defaultdict

class Solution:
    def countGoodNodes(self, edges: List[List[int]]) -> int:
        tree = defaultdict(list)

        for u, v in edges:
            tree[u].append(v)
            tree[v].append(u)

        self.good_nodes = 0

        def dfs(node, parent):
            subtree_sizes = []
            total_size = 1

            for child in tree[node]:
                if child != parent:
                    size = dfs(child, node)
                    subtree_sizes.append(size)
                    total_size += size

            if len(subtree_sizes) <= 1 or len(set(subtree_sizes)) == 1:
                self.good_nodes += 1

            return total_size

        dfs(0, -1)
        return self.good_nodes
```

---

### LeetCode 3

```python
class Solution:
    def firstMissingPositive(self, nums: List[int]) -> int:
        n = len(nums)

        for i in range(n):
            if nums[i] <= 0 or nums[i] > n:
                nums[i] = n + 1

        for i in range(n):
            num = abs(nums[i])
            if 1 <= num <= n:
                nums[num - 1] = -abs(nums[num - 1])

        for i in range(n):
            if nums[i] > 0:
                return i + 1

        return n + 1
```
