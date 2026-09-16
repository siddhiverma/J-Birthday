package main

import "fmt"

// Longest-valid template: at most k zeros.
func longestValid(a []int, k int) int {
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
	fmt.Println(longestValid([]int{1, 0, 1, 1, 0, 1}, 1))
}
