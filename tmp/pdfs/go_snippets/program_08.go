package main

import "fmt"

func longestUniqueBytes(s string) int {
	var freq [256]int
	left, answer := 0, 0
	for right := 0; right < len(s); right++ {
		incoming := s[right]
		freq[incoming]++
		for freq[incoming] > 1 {
			freq[s[left]]--
			left++
		}
		if length := right - left + 1; length > answer {
			answer = length
		}
	}
	return answer
}

func main() {
	fmt.Println(longestUniqueBytes("abcabcbb")) // ASCII/byte version
}
