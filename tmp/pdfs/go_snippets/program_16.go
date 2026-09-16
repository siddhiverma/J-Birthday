package main

import "fmt"

func productLessThanK(a []int, k int64) int64 {
	if k <= 1 {
		return 0
	}
	product := int64(1)
	left := 0
	var answer int64
	for right, value := range a {
		product *= int64(value)
		for product >= k {
			product /= int64(a[left])
			left++
		}
		answer += int64(right - left + 1)
	}
	return answer
}

func main() {
	fmt.Println(productLessThanK([]int{10, 5, 2, 6}, 100))
}
