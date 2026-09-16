package main

import "fmt"

func shortestSubarray(a []int, target int64) int {
	prefix := make([]int64, len(a)+1)
	for i, value := range a {
		prefix[i+1] = prefix[i] + int64(value)
	}
	deque := []int{}
	answer := len(a) + 1
	for i := 0; i <= len(a); i++ {
		for len(deque) > 0 && prefix[i]-prefix[deque[0]] >= target {
			if length := i - deque[0]; length < answer {
				answer = length
			}
			deque = deque[1:]
		}
		for len(deque) > 0 && prefix[deque[len(deque)-1]] >= prefix[i] {
			deque = deque[:len(deque)-1]
		}
		deque = append(deque, i)
	}
	if answer == len(a)+1 {
		return -1
	}
	return answer
}

func main() {
	fmt.Println(shortestSubarray([]int{2, -1, 2}, 3))
}
