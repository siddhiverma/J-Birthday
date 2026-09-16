package main

import "fmt"

// Monotonic-deque template instantiated for fixed-window maximum.
func windowMaximum(a []int, k int) []int {
	if k <= 0 || k > len(a) {
		return nil
	}
	deque, answer := []int{}, []int{}
	for right, value := range a {
		for len(deque) > 0 && a[deque[len(deque)-1]] <= value {
			deque = deque[:len(deque)-1]
		}
		deque = append(deque, right)
		left := right - k + 1
		if deque[0] < left {
			deque = deque[1:]
		}
		if left >= 0 {
			answer = append(answer, a[deque[0]])
		}
	}
	return answer
}

func main() {
	fmt.Println(windowMaximum([]int{1, 3, -1, -3, 5}, 3))
}
