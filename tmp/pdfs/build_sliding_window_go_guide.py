from pathlib import Path
import re
import subprocess

BASE = Path('tmp/pdfs/build_sliding_window_guide.py')
SNIPPETS = Path('tmp/pdfs/go_snippets')
SNIPPETS.mkdir(parents=True, exist_ok=True)

GO_PRIMER_PROGRAM = r'''package main

import "fmt"

func main() {
    nums := []int{2, 1, 5, 1, 3, 2} // slice: similar to vector<int>
    freq := make(map[int]int)        // hash map: similar to unordered_map
    window := 3
    sum := 0

    for right, value := range nums {
        sum += value
        freq[value]++
        if right >= window {
            outgoing := nums[right-window]
            sum -= outgoing
            freq[outgoing]--
            if freq[outgoing] == 0 {
                delete(freq, outgoing)
            }
        }
        if right >= window-1 {
            left := right - window + 1
            fmt.Printf("[%d,%d] sum=%d distinct=%d\n",
                left, right, sum, len(freq))
        }
    }
}'''

GO_BLOCKS = [
r'''package main

import (
    "errors"
    "fmt"
)

func maxSumK(a []int, k int) (int64, error) {
    if k <= 0 || k > len(a) {
        return 0, errors.New("invalid k")
    }
    var sum int64
    for i := 0; i < k; i++ {
        sum += int64(a[i])
    }
    answer := sum
    for right := k; right < len(a); right++ {
        sum += int64(a[right])
        sum -= int64(a[right-k])
        if sum > answer {
            answer = sum
        }
    }
    return answer, nil
}

func main() {
    answer, err := maxSumK([]int{2, 1, 5, 1, 3, 2}, 3)
    if err != nil {
        panic(err)
    }
    fmt.Println(answer) // 9
}''',
r'''package main

import "fmt"

func windowSums(a []int, k int) []int {
    if k <= 0 || k > len(a) {
        return nil
    }
    answer := []int{}
    left, sum := 0, 0
    for right, value := range a {
        sum += value // add incoming item
        if right-left+1 > k {
            sum -= a[left] // remove outgoing item
            left++
        }
        if right-left+1 == k {
            answer = append(answer, sum)
        }
    }
    return answer
}

func main() {
    fmt.Println(windowSums([]int{2, 1, 5, 1, 3, 2}, 3))
}''',
r'''package main

import "fmt"

func firstNegative(a []int, k int) []int {
    if k <= 0 || k > len(a) {
        return nil
    }
    queue := []int{} // indices of negative values
    answer := []int{}
    for right, value := range a {
        if value < 0 {
            queue = append(queue, right)
        }
        left := right - k + 1
        for len(queue) > 0 && queue[0] < left {
            queue = queue[1:]
        }
        if left >= 0 {
            if len(queue) == 0 {
                answer = append(answer, 0)
            } else {
                answer = append(answer, a[queue[0]])
            }
        }
    }
    return answer
}

func main() {
    a := []int{12, -1, -7, 8, -15, 30, 16, 28}
    fmt.Println(firstNegative(a, 3))
}''',
r'''package main

import "fmt"

func distinctPerWindow(a []int, k int) []int {
    if k <= 0 || k > len(a) {
        return nil
    }
    freq := make(map[int]int)
    answer := []int{}
    for right, value := range a {
        freq[value]++
        if right >= k {
            outgoing := a[right-k]
            freq[outgoing]--
            if freq[outgoing] == 0 {
                delete(freq, outgoing)
            }
        }
        if right >= k-1 {
            answer = append(answer, len(freq))
        }
    }
    return answer
}

func main() {
    fmt.Println(distinctPerWindow([]int{1, 2, 1, 3, 4, 2, 3}, 4))
}''',
r'''package main

import "fmt"

func longestSumAtMost(a []int, limit int64) int {
    left, answer := 0, 0
    var sum int64
    for right, value := range a {
        sum += int64(value)
        for left <= right && sum > limit {
            sum -= int64(a[left])
            left++
        }
        if length := right - left + 1; length > answer {
            answer = length
        }
    }
    return answer
}

func main() {
    // Correct because all values are non-negative.
    fmt.Println(longestSumAtMost([]int{2, 1, 5, 1, 1}, 7))
}''',
r'''package main

import "fmt"

func minLengthAtLeast(a []int, target int64) int {
    left, answer := 0, len(a)+1
    var sum int64
    for right, value := range a {
        sum += int64(value)
        for sum >= target {
            if length := right - left + 1; length < answer {
                answer = length
            }
            sum -= int64(a[left])
            left++
        }
    }
    if answer == len(a)+1 {
        return 0
    }
    return answer
}

func main() {
    fmt.Println(minLengthAtLeast([]int{2, 3, 1, 2, 4, 3}, 7))
}''',
r'''package main

import "fmt"

func longestOnes(a []int, k int) int {
    left, zeros, answer := 0, 0, 0
    for right, value := range a {
        if value == 0 {
            zeros++
        }
        for zeros > k {
            if a[left] == 0 {
                zeros--
            }
            left++
        }
        if length := right - left + 1; length > answer {
            answer = length
        }
    }
    return answer
}

func main() {
    a := []int{1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0}
    fmt.Println(longestOnes(a, 2))
}''',
r'''package main

import "fmt"

func longestUniqueBytes(s string) int {
    var freq [256]int
    left, answer := 0, 0
    for right := 0; right < len(s); right++ {
        incoming := s[right]
        freq[incoming]++
        for freq[incoming] > 1 {
            freq[s[left]]--
            left++
        }
        if length := right - left + 1; length > answer {
            answer = length
        }
    }
    return answer
}

func main() {
    fmt.Println(longestUniqueBytes("abcabcbb")) // ASCII/byte version
}''',
r'''package main

import "fmt"

func longestUniqueRunes(s string) int {
    chars := []rune(s) // Unicode code points
    last := make(map[rune]int)
    left, answer := 0, 0
    for right, char := range chars {
        if index, found := last[char]; found && index >= left {
            left = index + 1
        }
        last[char] = right
        if length := right - left + 1; length > answer {
            answer = length
        }
    }
    return answer
}

func main() {
    fmt.Println(longestUniqueRunes("aabca"))
}''',
r'''package main

import "fmt"

func findAnagrams(s, pattern string) []int {
    if len(pattern) == 0 || len(pattern) > len(s) {
        return nil
    }
    var need [256]int
    for i := 0; i < len(pattern); i++ {
        need[pattern[i]]++
    }
    missing, left := len(pattern), 0
    answer := []int{}
    for right := 0; right < len(s); right++ {
        incoming := s[right]
        if need[incoming] > 0 {
            missing--
        }
        need[incoming]--
        if right-left+1 > len(pattern) {
            outgoing := s[left]
            left++
            need[outgoing]++
            if need[outgoing] > 0 {
                missing++
            }
        }
        if missing == 0 {
            answer = append(answer, left)
        }
    }
    return answer
}

func main() {
    fmt.Println(findAnagrams("cbaebabacd", "abc"))
}''',
r'''package main

import "fmt"

func minWindow(s, target string) string {
    if len(target) == 0 || len(target) > len(s) {
        return ""
    }
    var need [256]int
    for i := 0; i < len(target); i++ {
        need[target[i]]++
    }
    missing, left := len(target), 0
    bestLeft, bestLen := 0, len(s)+1
    for right := 0; right < len(s); right++ {
        incoming := s[right]
        if need[incoming] > 0 {
            missing--
        }
        need[incoming]--
        for missing == 0 {
            if length := right - left + 1; length < bestLen {
                bestLeft, bestLen = left, length
            }
            outgoing := s[left]
            left++
            need[outgoing]++
            if need[outgoing] > 0 {
                missing++
            }
        }
    }
    if bestLen == len(s)+1 {
        return ""
    }
    return s[bestLeft : bestLeft+bestLen]
}

func main() {
    fmt.Println(minWindow("ADOBECODEBANC", "ABC"))
}''',
r'''package main

import "fmt"

func characterReplacement(s string, k int) int {
    var freq [26]int
    left, maxFreq, answer := 0, 0, 0
    for right := 0; right < len(s); right++ {
        index := s[right] - 'A'
        freq[index]++
        if freq[index] > maxFreq {
            maxFreq = freq[index]
        }
        for right-left+1-maxFreq > k {
            freq[s[left]-'A']--
            left++
        }
        if length := right - left + 1; length > answer {
            answer = length
        }
    }
    return answer
}

func main() {
    fmt.Println(characterReplacement("AABABBA", 1))
}''',
r'''package main

import "fmt"

func countAtMostKDistinct(a []int, k int) int64 {
    if k < 0 {
        return 0
    }
    freq := make(map[int]int)
    left, distinct := 0, 0
    var answer int64
    for right, value := range a {
        if freq[value] == 0 {
            distinct++
        }
        freq[value]++
        for distinct > k {
            outgoing := a[left]
            freq[outgoing]--
            if freq[outgoing] == 0 {
                delete(freq, outgoing)
                distinct--
            }
            left++
        }
        answer += int64(right - left + 1)
    }
    return answer
}

func main() {
    fmt.Println(countAtMostKDistinct([]int{1, 2, 1, 2, 3}, 2))
}''',
r'''package main

import "fmt"

func atMostDistinct(a []int, k int) int64 {
    if k < 0 {
        return 0
    }
    freq := make(map[int]int)
    left := 0
    var answer int64
    for right, value := range a {
        freq[value]++
        for len(freq) > k {
            outgoing := a[left]
            freq[outgoing]--
            if freq[outgoing] == 0 {
                delete(freq, outgoing)
            }
            left++
        }
        answer += int64(right - left + 1)
    }
    return answer
}

func exactlyKDistinct(a []int, k int) int64 {
    return atMostDistinct(a, k) - atMostDistinct(a, k-1)
}

func main() {
    fmt.Println(exactlyKDistinct([]int{1, 2, 1, 2, 3}, 2))
}''',
r'''package main

import "fmt"

func atMostSum(a []int, goal int) int64 {
    if goal < 0 {
        return 0
    }
    left, sum := 0, 0
    var answer int64
    for right, value := range a {
        sum += value
        for sum > goal {
            sum -= a[left]
            left++
        }
        answer += int64(right - left + 1)
    }
    return answer
}

func countBinarySum(a []int, goal int) int64 {
    return atMostSum(a, goal) - atMostSum(a, goal-1)
}

func main() {
    fmt.Println(countBinarySum([]int{1, 0, 1, 0, 1}, 2))
}''',
r'''package main

import "fmt"

func productLessThanK(a []int, k int64) int64 {
    if k <= 1 {
        return 0
    }
    product := int64(1)
    left := 0
    var answer int64
    for right, value := range a {
        product *= int64(value)
        for product >= k {
            product /= int64(a[left])
            left++
        }
        answer += int64(right - left + 1)
    }
    return answer
}

func main() {
    fmt.Println(productLessThanK([]int{10, 5, 2, 6}, 100))
}''',
r'''package main

import "fmt"

func maxSlidingWindow(a []int, k int) []int {
    if k <= 0 || k > len(a) {
        return nil
    }
    deque := []int{} // indices; values decrease front to back
    answer := []int{}
    for right, value := range a {
        for len(deque) > 0 && a[deque[len(deque)-1]] <= value {
            deque = deque[:len(deque)-1]
        }
        deque = append(deque, right)
        left := right - k + 1
        if deque[0] < left {
            deque = deque[1:]
        }
        if left >= 0 {
            answer = append(answer, a[deque[0]])
        }
    }
    return answer
}

func main() {
    a := []int{1, 3, -1, -3, 5, 3, 6, 7}
    fmt.Println(maxSlidingWindow(a, 3))
}''',
r'''package main

import "fmt"

func longestStable(a []int, limit int) int {
    maxQ, minQ := []int{}, []int{}
    left, answer := 0, 0
    for right, value := range a {
        for len(maxQ) > 0 && a[maxQ[len(maxQ)-1]] <= value {
            maxQ = maxQ[:len(maxQ)-1]
        }
        for len(minQ) > 0 && a[minQ[len(minQ)-1]] >= value {
            minQ = minQ[:len(minQ)-1]
        }
        maxQ = append(maxQ, right)
        minQ = append(minQ, right)
        for int64(a[maxQ[0]])-int64(a[minQ[0]]) > int64(limit) {
            if maxQ[0] == left {
                maxQ = maxQ[1:]
            }
            if minQ[0] == left {
                minQ = minQ[1:]
            }
            left++
        }
        if length := right - left + 1; length > answer {
            answer = length
        }
    }
    return answer
}

func main() {
    fmt.Println(longestStable([]int{8, 2, 4, 7}, 4))
}''',
r'''package main

import (
    "container/heap"
    "fmt"
)

type minHeap []int
func (h minHeap) Len() int           { return len(h) }
func (h minHeap) Less(i, j int) bool { return h[i] < h[j] }
func (h minHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *minHeap) Push(x any)        { *h = append(*h, x.(int)) }
func (h *minHeap) Pop() any {
    old := *h; x := old[len(old)-1]; *h = old[:len(old)-1]; return x
}

type maxHeap []int
func (h maxHeap) Len() int           { return len(h) }
func (h maxHeap) Less(i, j int) bool { return h[i] > h[j] }
func (h maxHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *maxHeap) Push(x any)        { *h = append(*h, x.(int)) }
func (h *maxHeap) Pop() any {
    old := *h; x := old[len(old)-1]; *h = old[:len(old)-1]; return x
}

type dualHeap struct {
    small maxHeap
    large minHeap
    delayed map[int]int
    smallSize, largeSize, k int
}

func newDualHeap(k int) *dualHeap {
    return &dualHeap{delayed: make(map[int]int), k: k}
}

func (d *dualHeap) pruneSmall() {
    for len(d.small) > 0 && d.delayed[d.small[0]] > 0 {
        value := heap.Pop(&d.small).(int)
        d.delayed[value]--
    }
}
func (d *dualHeap) pruneLarge() {
    for len(d.large) > 0 && d.delayed[d.large[0]] > 0 {
        value := heap.Pop(&d.large).(int)
        d.delayed[value]--
    }
}
func (d *dualHeap) balance() {
    if d.smallSize > d.largeSize+1 {
        heap.Push(&d.large, heap.Pop(&d.small))
        d.smallSize--; d.largeSize++; d.pruneSmall()
    } else if d.smallSize < d.largeSize {
        heap.Push(&d.small, heap.Pop(&d.large))
        d.smallSize++; d.largeSize--; d.pruneLarge()
    }
}
func (d *dualHeap) add(value int) {
    if len(d.small) == 0 || value <= d.small[0] {
        heap.Push(&d.small, value); d.smallSize++
    } else {
        heap.Push(&d.large, value); d.largeSize++
    }
    d.balance()
}
func (d *dualHeap) remove(value int) {
    d.delayed[value]++
    if value <= d.small[0] {
        d.smallSize--
        if value == d.small[0] { d.pruneSmall() }
    } else {
        d.largeSize--
        if len(d.large) > 0 && value == d.large[0] { d.pruneLarge() }
    }
    d.balance()
}
func (d *dualHeap) median() float64 {
    if d.k%2 == 1 { return float64(d.small[0]) }
    return (float64(d.small[0]) + float64(d.large[0])) / 2
}

func medians(a []int, k int) []float64 {
    if k <= 0 || k > len(a) { return nil }
    d := newDualHeap(k)
    answer := []float64{}
    for i, value := range a {
        d.add(value)
        if i >= k { d.remove(a[i-k]) }
        if i >= k-1 { answer = append(answer, d.median()) }
    }
    return answer
}

func main() {
    fmt.Println(medians([]int{1, 3, -1, -3, 5, 3, 6, 7}, 3))
}''',
r'''package main

import "fmt"

func subarraySumEqualsK(a []int, target int64) int64 {
    seen := map[int64]int64{0: 1}
    var prefix, answer int64
    for _, value := range a {
        prefix += int64(value)
        answer += seen[prefix-target]
        seen[prefix]++
    }
    return answer
}

func main() {
    fmt.Println(subarraySumEqualsK([]int{1, 1, 1}, 2))
}''',
r'''package main

import "fmt"

func shortestSubarray(a []int, target int64) int {
    prefix := make([]int64, len(a)+1)
    for i, value := range a {
        prefix[i+1] = prefix[i] + int64(value)
    }
    deque := []int{}
    answer := len(a) + 1
    for i := 0; i <= len(a); i++ {
        for len(deque) > 0 && prefix[i]-prefix[deque[0]] >= target {
            if length := i - deque[0]; length < answer {
                answer = length
            }
            deque = deque[1:]
        }
        for len(deque) > 0 && prefix[deque[len(deque)-1]] >= prefix[i] {
            deque = deque[:len(deque)-1]
        }
        deque = append(deque, i)
    }
    if answer == len(a)+1 {
        return -1
    }
    return answer
}

func main() {
    fmt.Println(shortestSubarray([]int{2, -1, 2}, 3))
}''',
r'''package main

import "fmt"

// Fixed-window template instantiated with sum as its state.
func fixedWindow(a []int, k int) []int {
    if k <= 0 || k > len(a) { return nil }
    left, sum := 0, 0
    answer := []int{}
    for right, value := range a {
        sum += value
        if right-left+1 > k { sum -= a[left]; left++ }
        if right-left+1 == k { answer = append(answer, sum) }
    }
    return answer
}

func main() {
    fmt.Println(fixedWindow([]int{1, 2, 3, 4, 5}, 3))
}''',
r'''package main

import "fmt"

// Longest-valid template: at most k zeros.
func longestValid(a []int, k int) int {
    left, zeros, answer := 0, 0, 0
    for right, value := range a {
        if value == 0 { zeros++ }
        for zeros > k {
            if a[left] == 0 { zeros-- }
            left++
        }
        if length := right-left+1; length > answer { answer = length }
    }
    return answer
}

func main() {
    fmt.Println(longestValid([]int{1, 0, 1, 1, 0, 1}, 1))
}''',
r'''package main

import "fmt"

// Shortest-valid template: positive values with sum at least target.
func shortestValid(a []int, target int) int {
    left, sum, answer := 0, 0, len(a)+1
    for right, value := range a {
        sum += value
        for sum >= target {
            if length := right-left+1; length < answer { answer = length }
            sum -= a[left]
            left++
        }
    }
    if answer == len(a)+1 { return 0 }
    return answer
}

func main() {
    fmt.Println(shortestValid([]int{2, 3, 1, 2, 4, 3}, 7))
}''',
r'''package main

import "fmt"

// Counting template: non-negative values with sum at most limit.
func countValid(a []int, limit int) int64 {
    left, sum := 0, 0
    var answer int64
    for right, value := range a {
        sum += value
        for sum > limit { sum -= a[left]; left++ }
        answer += int64(right-left+1)
    }
    return answer
}

func main() {
    fmt.Println(countValid([]int{1, 2, 1}, 3))
}''',
r'''package main

import "fmt"

func atMost(a []int, k int) int64 {
    if k < 0 { return 0 }
    freq := make(map[int]int)
    left := 0
    var answer int64
    for right, value := range a {
        freq[value]++
        for len(freq) > k {
            outgoing := a[left]
            freq[outgoing]--
            if freq[outgoing] == 0 { delete(freq, outgoing) }
            left++
        }
        answer += int64(right-left+1)
    }
    return answer
}

func exactlyK(a []int, k int) int64 {
    return atMost(a, k) - atMost(a, k-1)
}

func main() {
    fmt.Println(exactlyK([]int{1, 2, 1, 2, 3}, 2))
}''',
r'''package main

import "fmt"

// Monotonic-deque template instantiated for fixed-window maximum.
func windowMaximum(a []int, k int) []int {
    if k <= 0 || k > len(a) { return nil }
    deque, answer := []int{}, []int{}
    for right, value := range a {
        for len(deque) > 0 && a[deque[len(deque)-1]] <= value {
            deque = deque[:len(deque)-1]
        }
        deque = append(deque, right)
        left := right-k+1
        if deque[0] < left { deque = deque[1:] }
        if left >= 0 { answer = append(answer, a[deque[0]]) }
    }
    return answer
}

func main() {
    fmt.Println(windowMaximum([]int{1, 3, -1, -3, 5}, 3))
}''',
r'''package main

import "fmt"

// Brute-force oracle: longest subarray with sum <= limit.
func brute(a []int, limit int64) int {
    answer := 0
    for left := 0; left < len(a); left++ {
        var sum int64
        for right := left; right < len(a); right++ {
            sum += int64(a[right])
            if sum <= limit && right-left+1 > answer {
                answer = right-left+1
            }
        }
    }
    return answer
}

func main() {
    fmt.Println(brute([]int{2, 1, 5, 1, 1}, 7))
}''',
]

if len(GO_BLOCKS) != 28:
    raise RuntimeError(f'expected 28 Go blocks, found {len(GO_BLOCKS)}')

def gofmt(source):
    result = subprocess.run(['gofmt'], input=source, text=True,
                            capture_output=True, check=True)
    return result.stdout.rstrip()

GO_PRIMER_PROGRAM = gofmt(GO_PRIMER_PROGRAM)
GO_BLOCKS = [gofmt(source) for source in GO_BLOCKS]
DISPLAY_PRIMER_PROGRAM = GO_PRIMER_PROGRAM.replace('\t', '    ')
DISPLAY_GO_BLOCKS = [source.replace('\t', '    ') for source in GO_BLOCKS]

for index, source in enumerate([GO_PRIMER_PROGRAM] + GO_BLOCKS):
    (SNIPPETS / f'program_{index:02d}.go').write_text(source + '\n')

source = BASE.read_text()
pattern = re.compile(r"code\(r'''\n.*?'''\)", re.S)
counter = iter(DISPLAY_GO_BLOCKS)

def replace_code(_match):
    return "code(r'''\n" + next(counter) + "''')"

source, changed = pattern.subn(replace_code, source)
if changed != len(GO_BLOCKS):
    raise RuntimeError(f'expected 28 source blocks, replaced {changed}')

# The complete median program is intentionally long. Let only that listing split
# naturally across pages; keep every shorter program together.
source = source.replace(
    "def code(text):\n    story.append(KeepTogether([Preformatted(text.strip('\\n'), styles['CodeX'])]))",
    "def code(text):\n"
    "    item = Preformatted(text.strip('\\n'), styles['CodeX'])\n"
    "    if 'type dualHeap struct' in text:\n"
    "        story.append(item)\n"
    "    else:\n"
    "        story.append(KeepTogether([item]))",
)

replacements = {
    "output/pdf/sliding_window_dsa_complete_guide.pdf":
        "output/pdf/sliding_window_dsa_complete_go_guide.pdf",
    "SLIDING WINDOW - THE COMPLETE DSA GUIDE":
        "SLIDING WINDOW - THE COMPLETE GO DSA GUIDE",
    "A one-stop C++ reference and learning path":
        "A one-stop Go reference and learning path",
    "A one-stop C++ reference and learning path', 'Chapter'":
        "A one-stop Go reference and learning path', 'Chapter'",
    "C++ template catalog": "Go template catalog",
    "Use <code>long long</code> when sums may overflow int.":
        "Use <code>int64</code> when sums may exceed the machine-sized int range.",
    "A key with value zero still contributes to unordered_map::size().":
        "A key with value zero still contributes to len(freq) in Go.",
    "Use <code>unsigned char</code> when indexing a 256-entry array because plain <code>char</code> may be signed. For lowercase English letters, 26 entries are sufficient. For Unicode text, bytes are not characters; decode code points and use a map.":
        "Indexing a Go string returns bytes. A 256-entry array is ideal for ASCII/byte problems. For Unicode text, convert to []rune and use map[rune]int; byte indices and rune indices are different.",
    "Counts of subarrays can reach n(n+1)/2, so use <code>long long</code>.":
        "Counts can reach n(n+1)/2, so return <code>int64</code> even when indices use int.",
    "Deque versus heap versus multiset": "Deque versus heap versus ordered multiset",
    "Fixed-window median with two multisets": "Fixed-window median with two heaps",
    "Maintain a lower half <code>lo</code> and upper half <code>hi</code>. Every value in lo is no greater than every value in hi. Keep <code>lo.size() == hi.size()</code> or exactly one larger. The median is the largest value in lo, or the average of both boundary values.":
        "Maintain a max-heap for the lower half and a min-heap for the upper half. Keep the lower heap the same logical size as the upper heap or one larger. Because Go's container/heap does not support arbitrary deletion, mark outgoing values in a delayed-deletion map and prune them when they reach a heap top.",
    "Each insertion and deletion costs O(log k), so all medians cost O(n log k). With a multiset, <code>erase(value)</code> removes every equal occurrence; use <code>find</code> and erase the iterator to remove exactly one.":
        "Each logical insertion and deletion costs O(log k), so all medians cost O(n log k). The separate logical-size counters must ignore delayed entries that physically remain in a heap until pruning.",
    "array<int, 26/128/256>": "[26]int / [256]int",
    "unordered_map": "map",
    "map or multiset": "ordered tree (third-party) or heaps",
    "two multisets/heaps": "two heaps + delayed deletion",
    "multiset.erase(value)": "forget heap lazy deletion",
    "All duplicates erased": "stale outgoing values remain active",
    "Erase one iterator": "track delayed counts and logical sizes",
    "Use long long for sums/counts/products": "Use int64 for sums/counts/products",
    "<code>max</code> is essential.": "The <code>index >= left</code> test is essential.",
    "Use unsigned char": "Use byte values",
    "Balanced ordered halves": "Two heaps plus lazy deletion",
    "Two balanced multisets or heaps with lazy deletion": "Two heaps with lazy deletion",
    "two ordered halves plus sums of each half": "two heaps/ordered halves plus sums of each half",
    "C++ examples": "Go examples",
    "title='Sliding Window DSA Pattern - Complete Guide'":
        "title='Sliding Window DSA Pattern - Complete Go Guide'",
}
for old, new in replacements.items():
    source = source.replace(old, new)

# Replace C++-specific prose whose Python string literals span several lines.
source = re.sub(
    r"P\('Use <code>unsigned char</code>.*?points and use a map\.'\)",
    "P('Indexing a Go string returns bytes. A [256]int frequency array is ideal '"
    "  'for ASCII problems. For Unicode, convert once with []rune(s) and use a '"
    "  'map[rune]int; byte positions and rune positions are not interchangeable.')",
    source, flags=re.S,
)
source = re.sub(
    r"P\('Maintain a lower half <code>lo</code>.*?boundary values\.'\)",
    "P('Maintain a max-heap for the lower half and a min-heap for the upper half. '"
    "  'The lower half has the same logical size as the upper half or one more. '"
    "  'Go container/heap cannot delete an arbitrary outgoing value, so the '"
    "  'complete program uses delayed deletion and separate logical sizes.')",
    source, flags=re.S,
)
source = re.sub(
    r"P\('Each insertion and deletion costs O\(log k\).*?exactly one\.'\)",
    "P('Each logical insertion and deletion costs O(log k), so all medians cost '"
    "  'O(n log k). Delayed values may remain physically inside a heap until they '"
    "  'reach its top; pruning removes them before that top is queried.')",
    source, flags=re.S,
)
source = source.replace('Then a vector can replace a hash map.',
                        'Then a []int frequency slice can replace a map.')
source = source.replace("section('7.4 Deque versus heap versus ordered multiset')",
                        "section('7.4 Deque versus heap versus ordered structures')")
source = source.replace("('Multiset', 'O(log k)', 'Simple exact min/max and duplicates', 'Slower, erase one occurrence')",
                        "('Ordered tree', 'O(log k)', 'Exact min/max and duplicates', 'Requires a third-party Go package')")
source = source.replace("('Two multisets/heaps', 'O(log k)', 'Median and quantiles', 'Balancing is more complex')",
                        "('Two heaps', 'O(log k)', 'Median and quantiles', 'Needs balance and lazy deletion')")
source = source.replace('Two balanced multisets or heaps with lazy ',
                        'Two heaps with lazy ')
source = source.replace('two ordered halves plus sums of each half',
                        'two heaps/ordered halves plus their sums')

primer = r'''
# Go bridge chapter
chapter('Go for DSA - a bridge from C++',
        'Go has fewer containers and less syntax than C++, which makes the '
        'algorithm visible once a few language conventions become familiar.')
section('What changes when you move from C++ to Go?')
table(['C++ idea', 'Go equivalent', 'DSA note'], [
    ('vector<int>', '[]int', 'append(s, x); len(s); s[i]'),
    ('unordered_map<K,V>', 'map[K]V', 'Missing keys return the zero value'),
    ('array<int,256>', '[256]int', 'Zero-initialized automatically'),
    ('deque<int>', '[]int used as a deque', 'Append at back; reslice or use a head index'),
    ('priority_queue', 'container/heap', 'Implement five interface methods'),
    ('long long', 'int64', 'Convert explicitly: int64(x)'),
    ('pair / tuple', 'small struct', 'Named fields improve readability'),
    ('exceptions', 'error return or panic', 'Validate k at API boundaries'),
], [45 * mm, 49 * mm, 80 * mm], font=7.3)

section('The Go rules that matter most for sliding windows')
bullets([
    '<b>Arrays and slices differ:</b> [256]int has fixed length; []int is a '
    'dynamic view backed by an array.',
    '<b>Maps return zero for missing keys:</b> freq[x]++ works immediately. Use '
    'value, found := m[key] when presence itself matters, and delete(m, key) to '
    'remove a key.',
    '<b>Strings are byte sequences:</b> s[i] is a byte. Use []rune(s) for Unicode '
    'code points. Most interview problems specify ASCII or English letters.',
    '<b>No ternary operator:</b> use a normal if statement. Go favors explicit '
    'control flow.',
    '<b>Unused imports and variables are compile errors:</b> this catches clutter '
    'but surprises new Go users.',
    '<b>int is machine-sized:</b> indices naturally use int; large sums and counts '
    'should use int64 with explicit conversions.',
])

section('A complete first Go window program')
P('Every listing in this edition follows the same executable shape: package '
  'declaration, imports, algorithm function, and main with a small example. Save '
  'a listing as <code>main.go</code> and run <code>go run main.go</code>.')
code(r"""__GO_PRIMER_PROGRAM__""")

section('Reading Go algorithm code quickly')
P('<code>for right, value := range nums</code> yields an index and a copy of the '
  'value. <code>:=</code> declares variables using inferred types. Multiple '
  'assignment such as <code>left, sum := 0, 0</code> is common. Slices use '
  'half-open bounds: <code>s[a:b]</code> includes a and excludes b. Functions may '
  'return multiple values, which is useful for returning an answer plus an error.')
callout('C++ habit to unlearn',
        'Do not search for a Go STL equivalent for every C++ container. For '
        'sliding windows, slices, arrays, maps, and container/heap cover nearly '
        'everything. A slice of indices is the usual deque representation.', 'orange')

'''.replace('__GO_PRIMER_PROGRAM__', DISPLAY_PRIMER_PROGRAM)
source = source.replace('# Chapter 1\n', primer + '# Chapter 1\n', 1)

namespace = {'GO_PRIMER_PROGRAM': GO_PRIMER_PROGRAM}
exec(compile(source, str(BASE), 'exec'), namespace)
