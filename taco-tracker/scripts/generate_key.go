package main

import (
	"fmt"
	"taco-tracker/pkg/auth"
)

func main() {
	fmt.Println(auth.GenerateRandomKey())
}
