package main

import "fmt"

func longestUniqueRunes(s string) int {
	chars := []rune(s) // Unicode code points
	last := make(map[rune]int)
	left, answer := 0, 0
	for right, char := range chars {
		if index, found := last[char]; found && index >= left {
			left = index + 1
		}
		last[char] = right
		if length := right - left + 1; length > answer {
			answer = length
		}
	}
	return answer
}

func main() {
	fmt.Println(longestUniqueRunes("aabca"))
}
