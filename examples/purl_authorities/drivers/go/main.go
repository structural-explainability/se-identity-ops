// main.go - Run packageurl-go on the corpus and print one JSON array.
//
// WHAT: Reads corpus.csv (row, set_id, family, input). For each input it calls
//       packageurl.FromString and then ToString, and records the normalized string
//       or the error text.
// WHY:  An independently developed implementation of the Package URL specification,
//       used as a second authority for the same operation as packageurl-python.
// OBS:  This file adds no normalization rules of its own.
package main

import (
	"encoding/csv"
	"encoding/json"
	"os"

	"github.com/package-url/packageurl-go"
)

type result struct {
	Row    string `json:"row"`
	OK     bool   `json:"ok"`
	Output string `json:"output"`
	Error  string `json:"error"`
}

func main() {
	file, err := os.Open(os.Args[1])
	if err != nil {
		panic(err)
	}
	defer file.Close()
	records, err := csv.NewReader(file).ReadAll()
	if err != nil {
		panic(err)
	}
	results := []result{}
	for _, record := range records[1:] {
		item := result{Row: record[0]}
		parsed, parseErr := packageurl.FromString(record[3])
		if parseErr != nil {
			item.Error = parseErr.Error()
		} else {
			item.OK = true
			item.Output = parsed.ToString()
		}
		results = append(results, item)
	}
	encoder := json.NewEncoder(os.Stdout)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(results); err != nil {
		panic(err)
	}
}
