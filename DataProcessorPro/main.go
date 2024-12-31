package main

import (
	"encoding/csv"
	"fmt"
	"math/rand"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"sync"
	"time"

	"github.com/schollz/progressbar/v3"
	"github.com/xuri/excelize/v2"
)

// Configuration struct for processing options
type ProcessConfig struct {
	BatchSize    int
	NumWorkers   int
	UseBuffering bool
	Method       string // "sequential", "concurrent", "batch"
}

// Metrics for performance tracking
type PerformanceMetrics struct {
	StartTime   time.Time
	EndTime     time.Time
	RowsHandled int
	MemoryUsed  uint64
	Method      string
}

func (pm *PerformanceMetrics) Duration() time.Duration {
	return pm.EndTime.Sub(pm.StartTime)
}

// Educational wrapper to demonstrate different processing methods
func demonstrateProcessingMethods(inputFile string) {
	fmt.Println("🎓 Educational Data Processing Algorithm Demo")
	fmt.Println("============================================")

	// Load data once
	data := loadExcelData(inputFile)

	// Run and measure different methods
	methods := []ProcessConfig{
		{Method: "sequential", BatchSize: 1, NumWorkers: 1, UseBuffering: false},
		{Method: "concurrent", BatchSize: 1, NumWorkers: runtime.NumCPU(), UseBuffering: true},
		{Method: "batch", BatchSize: 1000, NumWorkers: runtime.NumCPU(), UseBuffering: true},
	}

	var results []PerformanceMetrics

	for _, config := range methods {
		fmt.Printf("\n📊 Testing %s method...\n", config.Method)
		metric := processData(data, config)
		results = append(results, metric)

		// Clear previous output files
		os.Remove("VA_" + config.Method + ".csv")
		os.Remove("VB_" + config.Method + ".csv")
	}

	// Display comparative results
	displayResults(results)
}

func processData(data [][]string, config ProcessConfig) PerformanceMetrics {
	metrics := PerformanceMetrics{
		StartTime: time.Now(),
		Method:    config.Method,
	}

	switch config.Method {
	case "sequential":
		processSequential(data)
	case "concurrent":
		processConcurrent(data, config.NumWorkers)
	case "batch":
		processBatch(data, config.BatchSize, config.NumWorkers)
	}

	metrics.EndTime = time.Now()
	metrics.RowsHandled = len(data)

	var m runtime.MemStats
	runtime.ReadMemStats(&m)
	metrics.MemoryUsed = m.Alloc

	return metrics
}

// Sequential Processing Method
func processSequential(data [][]string) {
	fmt.Println("🔄 Sequential Processing")
	fmt.Println("   - Single thread")
	fmt.Println("   - No buffering")
	fmt.Println("   - Simple but slower for large datasets")

	r := rand.New(rand.NewSource(99))
	totalRows := len(data)
	splitPoint := totalRows / 2

	if totalRows%2 != 0 && r.Float32() < 0.5 {
		splitPoint++
	}

	writeCSVWithProgress("VA_sequential.csv", data[:splitPoint], "Sequential VA")
	writeCSVWithProgress("VB_sequential.csv", data[splitPoint:], "Sequential VB")
}

// Concurrent Processing Method
func processConcurrent(data [][]string, numWorkers int) {
	fmt.Println("⚡ Concurrent Processing")
	fmt.Println("   - Multiple goroutines")
	fmt.Println("   - Buffered channels")
	fmt.Println("   - Better for I/O-bound tasks")
	fmt.Printf("   - Using %d workers\n", numWorkers)

	r := rand.New(rand.NewSource(99))
	totalRows := len(data)
	splitPoint := totalRows / 2

	if totalRows%2 != 0 && r.Float32() < 0.5 {
		splitPoint++
	}

	var wg sync.WaitGroup

	// Create buffered channels for work distribution
	resultsA := make(chan []string, numWorkers)
	resultsB := make(chan []string, numWorkers)

	// Start worker pools for both files
	for i := 0; i < numWorkers; i++ {
		wg.Add(2)

		// Workers for VA file
		go func(workerID int) {
			defer wg.Done()
			fileA, err := os.OpenFile("VA_concurrent.csv", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
			if err != nil {
				fmt.Printf("Worker %d VA error: %v\n", workerID, err)
				return
			}
			defer fileA.Close()

			writerA := csv.NewWriter(fileA)
			defer writerA.Flush()

			for row := range resultsA {
				if err := writerA.Write(row); err != nil {
					fmt.Printf("Worker %d VA write error: %v\n", workerID, err)
				}
			}
		}(i)

		// Workers for VB file
		go func(workerID int) {
			defer wg.Done()
			fileB, err := os.OpenFile("VB_concurrent.csv", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
			if err != nil {
				fmt.Printf("Worker %d VB error: %v\n", workerID, err)
				return
			}
			defer fileB.Close()

			writerB := csv.NewWriter(fileB)
			defer writerB.Flush()

			for row := range resultsB {
				if err := writerB.Write(row); err != nil {
					fmt.Printf("Worker %d VB write error: %v\n", workerID, err)
				}
			}
		}(i)
	}

	// Create progress bars
	barA := progressbar.Default(int64(splitPoint), "Concurrent VA")
	barB := progressbar.Default(int64(totalRows-splitPoint), "Concurrent VB")

	// Distribute data to appropriate channels
	go func() {
		for i, row := range data[:splitPoint] {
			resultsA <- row
			barA.Add(1)
			if i%100 == 0 { // Add some artificial delay to demonstrate concurrent processing
				time.Sleep(time.Microsecond)
			}
		}
		close(resultsA)
	}()

	go func() {
		for i, row := range data[splitPoint:] {
			resultsB <- row
			barB.Add(1)
			if i%100 == 0 { // Add some artificial delay to demonstrate concurrent processing
				time.Sleep(time.Microsecond)
			}
		}
		close(resultsB)
	}()

	wg.Wait()
}

// Batch Processing Method
func processBatch(data [][]string, batchSize, numWorkers int) {
	fmt.Println("📦 Batch Processing")
	fmt.Println("   - Processing in chunks")
	fmt.Println("   - Worker pool pattern")
	fmt.Println("   - Best for large datasets")

	r := rand.New(rand.NewSource(99))
	totalRows := len(data)
	splitPoint := totalRows / 2

	if totalRows%2 != 0 && r.Float32() < 0.5 {
		splitPoint++
	}

	// Create worker pools
	var wg sync.WaitGroup
	jobs := make(chan [][]string, numWorkers)
	results := make(chan [][]string, numWorkers)

	// Start worker pool
	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		go batchWorker(jobs, results, &wg)
	}

	// Split data into batches and send to workers
	go func() {
		for i := 0; i < len(data); i += batchSize {
			end := i + batchSize
			if end > len(data) {
				end = len(data)
			}
			jobs <- data[i:end]
		}
		close(jobs)
	}()

	// Collect and write results
	writeCSVBatched("VA_batch.csv", "VB_batch.csv", results, totalRows, "Batch Processing")
	wg.Wait()
}

func batchWorker(jobs <-chan [][]string, results chan<- [][]string, wg *sync.WaitGroup) {
	defer wg.Done()
	for batch := range jobs {
		// Process batch
		results <- batch
	}
}

// Helper functions
func loadExcelData(filename string) [][]string {
	xlsx, err := excelize.OpenFile(filename)
	if err != nil {
		panic(err)
	}
	defer xlsx.Close()

	rows, err := xlsx.GetRows(xlsx.GetSheetList()[0])
	if err != nil {
		panic(err)
	}
	return rows[1:] // Skip header
}

func writeCSVWithProgress(filename string, data [][]string, label string) {
	file, _ := os.Create(filename)
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	bar := progressbar.Default(int64(len(data)), label)

	for _, row := range data {
		writer.Write(row)
		bar.Add(1)
	}
}

// func writeCSVBuffered(filename string, data [][]string, results chan []string, label string) {
// 	file, _ := os.Create(filename)
// 	defer file.Close()

// 	writer := csv.NewWriter(file)
// 	defer writer.Flush()

// 	bar := progressbar.Default(int64(len(data)), label)

// 	for _, row := range data {
// 		writer.Write(row)
// 		results <- row
// 		bar.Add(1)
// 	}
// }

func writeCSVBatched(filenameA, filenameB string, results chan [][]string, totalRows int, label string) {
	fileA, _ := os.Create(filenameA)
	fileB, _ := os.Create(filenameB)
	defer fileA.Close()
	defer fileB.Close()

	writerA := csv.NewWriter(fileA)
	writerB := csv.NewWriter(fileB)
	defer writerA.Flush()
	defer writerB.Flush()

	bar := progressbar.Default(int64(totalRows), label)

	for batch := range results {
		for _, row := range batch {
			if rand.Float32() < 0.5 {
				writerA.Write(row)
			} else {
				writerB.Write(row)
			}
			bar.Add(1)
		}
	}
}

func displayResults(metrics []PerformanceMetrics) {
	fmt.Println("\n📈 Performance Comparison")
	fmt.Println("========================")

	fmt.Printf("%-12s | %-10s | %-15s | %-10s\n",
		"Method", "Duration", "Rows/Second", "Memory Used")
	fmt.Println("------------------------------------------------")

	for _, m := range metrics {
		rowsPerSec := float64(m.RowsHandled) / m.Duration().Seconds()
		memoryMB := float64(m.MemoryUsed) / 1024 / 1024

		fmt.Printf("%-12s | %-10s | %-15.2f | %-10.2f MB\n",
			m.Method,
			m.Duration().Round(time.Millisecond),
			rowsPerSec,
			memoryMB)
	}
}

func main() {
	// Get the actual program name from os.Args[0]
	progName := filepath.Base(os.Args[0])

	// Strip .exe extension if present for help message formatting
	displayName := strings.TrimSuffix(progName, ".exe")

	if len(os.Args) != 2 {
		fmt.Printf("Usage: go run %s <sequential_output.xlsx>\n", displayName)
		fmt.Println("\nExample:")
		fmt.Printf("  go run %s data.xlsx\n", displayName)
		fmt.Println("\nNote: The input file must be an Excel (.xlsx) file")
		return
	}

	// Verify file exists and has correct extension
	inputFile := os.Args[1]
	if !strings.HasSuffix(strings.ToLower(inputFile), ".xlsx") {
		fmt.Printf("Error: Input file must be an Excel (.xlsx) file\n")
		return
	}

	// Check if file exists
	if _, err := os.Stat(inputFile); os.IsNotExist(err) {
		fmt.Printf("Error: File '%s' does not exist\n", inputFile)
		return
	}

	// Create output directory if it doesn't exist
	outputDir := "output"
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		fmt.Printf("Error creating output directory: %v\n", err)
		return
	}

	fmt.Println("🚀 Starting data processing demonstration...")
	demonstrateProcessingMethods(inputFile)
}

// go run main.go sequential_output.xlsx
// go run main.exe sequential_output.xlsx
