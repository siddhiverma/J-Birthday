package main

import (
	"container/heap"
	"fmt"
)

type minHeap []int

func (h minHeap) Len() int           { return len(h) }
func (h minHeap) Less(i, j int) bool { return h[i] < h[j] }
func (h minHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *minHeap) Push(x any)        { *h = append(*h, x.(int)) }
func (h *minHeap) Pop() any {
	old := *h
	x := old[len(old)-1]
	*h = old[:len(old)-1]
	return x
}

type maxHeap []int

func (h maxHeap) Len() int           { return len(h) }
func (h maxHeap) Less(i, j int) bool { return h[i] > h[j] }
func (h maxHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *maxHeap) Push(x any)        { *h = append(*h, x.(int)) }
func (h *maxHeap) Pop() any {
	old := *h
	x := old[len(old)-1]
	*h = old[:len(old)-1]
	return x
}

type dualHeap struct {
	small                   maxHeap
	large                   minHeap
	delayed                 map[int]int
	smallSize, largeSize, k int
}

func newDualHeap(k int) *dualHeap {
	return &dualHeap{delayed: make(map[int]int), k: k}
}

func (d *dualHeap) pruneSmall() {
	for len(d.small) > 0 && d.delayed[d.small[0]] > 0 {
		value := heap.Pop(&d.small).(int)
		d.delayed[value]--
	}
}
func (d *dualHeap) pruneLarge() {
	for len(d.large) > 0 && d.delayed[d.large[0]] > 0 {
		value := heap.Pop(&d.large).(int)
		d.delayed[value]--
	}
}
func (d *dualHeap) balance() {
	if d.smallSize > d.largeSize+1 {
		heap.Push(&d.large, heap.Pop(&d.small))
		d.smallSize--
		d.largeSize++
		d.pruneSmall()
	} else if d.smallSize < d.largeSize {
		heap.Push(&d.small, heap.Pop(&d.large))
		d.smallSize++
		d.largeSize--
		d.pruneLarge()
	}
}
func (d *dualHeap) add(value int) {
	if len(d.small) == 0 || value <= d.small[0] {
		heap.Push(&d.small, value)
		d.smallSize++
	} else {
		heap.Push(&d.large, value)
		d.largeSize++
	}
	d.balance()
}
func (d *dualHeap) remove(value int) {
	d.delayed[value]++
	if value <= d.small[0] {
		d.smallSize--
		if value == d.small[0] {
			d.pruneSmall()
		}
	} else {
		d.largeSize--
		if len(d.large) > 0 && value == d.large[0] {
			d.pruneLarge()
		}
	}
	d.balance()
}
func (d *dualHeap) median() float64 {
	if d.k%2 == 1 {
		return float64(d.small[0])
	}
	return (float64(d.small[0]) + float64(d.large[0])) / 2
}

func medians(a []int, k int) []float64 {
	if k <= 0 || k > len(a) {
		return nil
	}
	d := newDualHeap(k)
	answer := []float64{}
	for i, value := range a {
		d.add(value)
		if i >= k {
			d.remove(a[i-k])
		}
		if i >= k-1 {
			answer = append(answer, d.median())
		}
	}
	return answer
}

func main() {
	fmt.Println(medians([]int{1, 3, -1, -3, 5, 3, 6, 7}, 3))
}
