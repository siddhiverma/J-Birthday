package main

import "fmt"

func findAnagrams(s, pattern string) []int {
	if len(pattern) == 0 || len(pattern) > len(s) {
		return nil
	}
	var need [256]int
	for i := 0; i < len(pattern); i++ {
		need[pattern[i]]++
	}
	missing, left := len(pattern), 0
	answer := []int{}
	for right := 0; right < len(s); right++ {
		incoming := s[right]
		if need[incoming] > 0 {
			missing--
		}
		need[incoming]--
		if right-left+1 > len(pattern) {
			outgoing := s[left]
			left++
			need[outgoing]++
			if need[outgoing] > 0 {
				missing++
			}
		}
		if missing == 0 {
			answer = append(answer, left)
		}
	}
	return answer
}

func main() {
	fmt.Println(findAnagrams("cbaebabacd", "abc"))
}
