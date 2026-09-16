package main

import "fmt"

func characterReplacement(s string, k int) int {
	var freq [26]int
	left, maxFreq, answer := 0, 0, 0
	for right := 0; right < len(s); right++ {
		index := s[right] - 'A'
		freq[index]++
		if freq[index] > maxFreq {
			maxFreq = freq[index]
		}
		for right-left+1-maxFreq > k {
			freq[s[left]-'A']--
			left++
		}
		if length := right - left + 1; length > answer {
			answer = length
		}
	}
	return answer
}

func main() {
	fmt.Println(characterReplacement("AABABBA", 1))
}
