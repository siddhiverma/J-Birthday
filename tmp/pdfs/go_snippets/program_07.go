package main

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
}
