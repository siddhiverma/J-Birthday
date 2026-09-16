package main

import "fmt"

// Counting template: non-negative values with sum at most limit.
func countValid(a []int, limit int) int64 {
	left, sum := 0, 0
	var answer int64
	for right, value := range a {
		sum += value
		for sum > limit {
			sum -= a[left]
			left++
		}
		answer += int64(right - left + 1)
	}
	return answer
}

func main() {
	fmt.Println(countValid([]int{1, 2, 1}, 3))
}
