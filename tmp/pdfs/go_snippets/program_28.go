package main

import "fmt"

// Brute-force oracle: longest subarray with sum <= limit.
func brute(a []int, limit int64) int {
	answer := 0
	for left := 0; left < len(a); left++ {
		var sum int64
		for right := left; right < len(a); right++ {
			sum += int64(a[right])
			if sum <= limit && right-left+1 > answer {
				answer = right - left + 1
			}
		}
	}
	return answer
}

func main() {
	fmt.Println(brute([]int{2, 1, 5, 1, 1}, 7))
}
