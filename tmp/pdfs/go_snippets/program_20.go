package main

import "fmt"

func subarraySumEqualsK(a []int, target int64) int64 {
	seen := map[int64]int64{0: 1}
	var prefix, answer int64
	for _, value := range a {
		prefix += int64(value)
		answer += seen[prefix-target]
		seen[prefix]++
	}
	return answer
}

func main() {
	fmt.Println(subarraySumEqualsK([]int{1, 1, 1}, 2))
}
