package main

import "fmt"

// Shortest-valid template: positive values with sum at least target.
func shortestValid(a []int, target int) int {
	left, sum, answer := 0, 0, len(a)+1
	for right, value := range a {
		sum += value
		for sum >= target {
			if length := right - left + 1; length < answer {
				answer = length
			}
			sum -= a[left]
			left++
		}
	}
	if answer == len(a)+1 {
		return 0
	}
	return answer
}

func main() {
	fmt.Println(shortestValid([]int{2, 3, 1, 2, 4, 3}, 7))
}
