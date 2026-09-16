package main

import "fmt"

func longestStable(a []int, limit int) int {
	maxQ, minQ := []int{}, []int{}
	left, answer := 0, 0
	for right, value := range a {
		for len(maxQ) > 0 && a[maxQ[len(maxQ)-1]] <= value {
			maxQ = maxQ[:len(maxQ)-1]
		}
		for len(minQ) > 0 && a[minQ[len(minQ)-1]] >= value {
			minQ = minQ[:len(minQ)-1]
		}
		maxQ = append(maxQ, right)
		minQ = append(minQ, right)
		for int64(a[maxQ[0]])-int64(a[minQ[0]]) > int64(limit) {
			if maxQ[0] == left {
				maxQ = maxQ[1:]
			}
			if minQ[0] == left {
				minQ = minQ[1:]
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
	fmt.Println(longestStable([]int{8, 2, 4, 7}, 4))
}
