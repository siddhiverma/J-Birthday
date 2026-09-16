package main

import "fmt"

func firstNegative(a []int, k int) []int {
	if k <= 0 || k > len(a) {
		return nil
	}
	queue := []int{} // indices of negative values
	answer := []int{}
	for right, value := range a {
		if value < 0 {
			queue = append(queue, right)
		}
		left := right - k + 1
		for len(queue) > 0 && queue[0] < left {
			queue = queue[1:]
		}
		if left >= 0 {
			if len(queue) == 0 {
				answer = append(answer, 0)
			} else {
				answer = append(answer, a[queue[0]])
			}
		}
	}
	return answer
}

func main() {
	a := []int{12, -1, -7, 8, -15, 30, 16, 28}
	fmt.Println(firstNegative(a, 3))
}
