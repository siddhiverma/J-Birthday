package main

import "fmt"

func minLengthAtLeast(a []int, target int64) int {
	left, answer := 0, len(a)+1
	var sum int64
	for right, value := range a {
		sum += int64(value)
		for sum >= target {
			if length := right - left + 1; length < answer {
				answer = length
			}
			sum -= int64(a[left])
			left++
		}
	}
	if answer == len(a)+1 {
		return 0
	}
	return answer
}

func main() {
	fmt.Println(minLengthAtLeast([]int{2, 3, 1, 2, 4, 3}, 7))
}
