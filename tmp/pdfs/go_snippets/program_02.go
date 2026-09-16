package main

import "fmt"

func windowSums(a []int, k int) []int {
	if k <= 0 || k > len(a) {
		return nil
	}
	answer := []int{}
	left, sum := 0, 0
	for right, value := range a {
		sum += value // add incoming item
		if right-left+1 > k {
			sum -= a[left] // remove outgoing item
			left++
		}
		if right-left+1 == k {
			answer = append(answer, sum)
		}
	}
	return answer
}

func main() {
	fmt.Println(windowSums([]int{2, 1, 5, 1, 3, 2}, 3))
}
