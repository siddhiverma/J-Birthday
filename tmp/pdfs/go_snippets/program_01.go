package main

import (
	"errors"
	"fmt"
)

func maxSumK(a []int, k int) (int64, error) {
	if k <= 0 || k > len(a) {
		return 0, errors.New("invalid k")
	}
	var sum int64
	for i := 0; i < k; i++ {
		sum += int64(a[i])
	}
	answer := sum
	for right := k; right < len(a); right++ {
		sum += int64(a[right])
		sum -= int64(a[right-k])
		if sum > answer {
			answer = sum
		}
	}
	return answer, nil
}

func main() {
	answer, err := maxSumK([]int{2, 1, 5, 1, 3, 2}, 3)
	if err != nil {
		panic(err)
	}
	fmt.Println(answer) // 9
}
