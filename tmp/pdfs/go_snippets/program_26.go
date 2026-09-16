package main

import "fmt"

func atMost(a []int, k int) int64 {
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

func exactlyK(a []int, k int) int64 {
	return atMost(a, k) - atMost(a, k-1)
}

func main() {
	fmt.Println(exactlyK([]int{1, 2, 1, 2, 3}, 2))
}
