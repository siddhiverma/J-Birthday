package main

import "fmt"

// Fixed-window template instantiated with sum as its state.
func fixedWindow(a []int, k int) []int {
	if k <= 0 || k > len(a) {
		return nil
	}
	left, sum := 0, 0
	answer := []int{}
	for right, value := range a {
		sum += value
		if right-left+1 > k {
			sum -= a[left]
			left++
		}
		if right-left+1 == k {
			answer = append(answer, sum)
		}
	}
	return answer
}

func main() {
	fmt.Println(fixedWindow([]int{1, 2, 3, 4, 5}, 3))
}
