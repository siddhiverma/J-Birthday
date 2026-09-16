package main

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
}
