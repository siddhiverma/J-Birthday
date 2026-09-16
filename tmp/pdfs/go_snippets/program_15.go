package main

import "fmt"

func atMostSum(a []int, goal int) int64 {
	if goal < 0 {
		return 0
	}
	left, sum := 0, 0
	var answer int64
	for right, value := range a {
		sum += value
		for sum > goal {
			sum -= a[left]
			left++
		}
		answer += int64(right - left + 1)
	}
	return answer
}

func countBinarySum(a []int, goal int) int64 {
	return atMostSum(a, goal) - atMostSum(a, goal-1)
}

func main() {
	fmt.Println(countBinarySum([]int{1, 0, 1, 0, 1}, 2))
}
