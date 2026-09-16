package main

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
}
