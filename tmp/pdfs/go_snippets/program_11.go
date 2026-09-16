package main

import "fmt"

func minWindow(s, target string) string {
	if len(target) == 0 || len(target) > len(s) {
		return ""
	}
	var need [256]int
	for i := 0; i < len(target); i++ {
		need[target[i]]++
	}
	missing, left := len(target), 0
	bestLeft, bestLen := 0, len(s)+1
	for right := 0; right < len(s); right++ {
		incoming := s[right]
		if need[incoming] > 0 {
			missing--
		}
		need[incoming]--
		for missing == 0 {
			if length := right - left + 1; length < bestLen {
				bestLeft, bestLen = left, length
			}
			outgoing := s[left]
			left++
			need[outgoing]++
			if need[outgoing] > 0 {
				missing++
			}
		}
	}
	if bestLen == len(s)+1 {
		return ""
	}
	return s[bestLeft : bestLeft+bestLen]
}

func main() {
	fmt.Println(minWindow("ADOBECODEBANC", "ABC"))
}
