package main

import "fmt"

func main() {
	nums := []int{2, 1, 5, 1, 3, 2} // slice: similar to vector<int>
	freq := make(map[int]int)       // hash map: similar to unordered_map
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
}
