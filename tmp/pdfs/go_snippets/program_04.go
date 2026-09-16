package main

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
}
