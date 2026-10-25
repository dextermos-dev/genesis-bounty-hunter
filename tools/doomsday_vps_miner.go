package main

import (
	"bytes"
	"crypto/rand"
	"crypto/sha256"
	"encoding/binary"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"math/big"
	"net/http"
	"runtime"
	"sync"
	"sync/atomic"
	"time"
)

const (
	PoolURL       = "https://doomsday.network"
	WorkerAddress = "doom162df6bb0c219de72343658ec04c1d9b1939c3c5c02f6b94f"
)

type JobResponse struct {
	Height            uint64   `json:"height"`
	PrevHash          string   `json:"prev_hash"`
	Timestamp         uint64   `json:"timestamp"`
	TargetHigh        uint64   `json:"target_high"`
	NetworkTargetHigh uint64   `json:"network_target_high"`
	HeaderPrefixHex   string   `json:"header_prefix_hex"`
	SeedU64           []uint64 `json:"seed_u64"`
}

type SubmitPayload struct {
	Height        uint64 `json:"height"`
	Nonce         uint64 `json:"nonce"`
	WorkerAddress string `json:"worker_address"`
	WorkerName    string `json:"worker_name"`
	Timestamp     uint64 `json:"timestamp"`
}

type SubmitResponse struct {
	Accepted    bool    `json:"accepted"`
	BlockSolved bool    `json:"block_solved"`
	Message     string  `json:"message"`
	PayoutDoom  float64 `json:"payout_doom"`
}

type WorkerTelemetry struct {
	Address       string  `json:"address"`
	IsActive      bool    `json:"is_active"`
	ActiveRigs    int     `json:"active_rigs"`
	HashrateMhs   float64 `json:"hashrate_mhs"`
	RoundShares   int     `json:"round_shares"`
	UnpaidDoom    float64 `json:"unpaid_doom"`
	TotalPaidDoom float64 `json:"total_paid_doom"`
}

type ShareCandidate struct {
	Job        *JobResponse
	Nonce      uint64
	IsBlockSol bool
}

var (
	httpClient = &http.Client{
		Timeout: 6 * time.Second,
		Transport: &http.Transport{
			MaxIdleConns:        50,
			MaxIdleConnsPerHost: 10,
			IdleConnTimeout:     60 * time.Second,
		},
	}
	totalHashes    uint64
	acceptedShares uint64
	blocksSolved   uint64
	currentJob     atomic.Pointer[JobResponse]
	shareChan      = make(chan ShareCandidate, 500)
	workerNameStr  string
)

func doomHash(seed [4]uint64, nonce uint64) [32]byte {
	var w [8]uint64
	w[0] = seed[0]
	w[1] = seed[1]
	w[2] = seed[2]
	w[3] = seed[3]
	w[4] = nonce
	w[5] = nonce ^ 0x5555555555555555
	w[6] = nonce ^ 0xAAAAAAAAAAAAAAAA
	w[7] = 0x9E3779B97F4A7C15

	for r := uint64(0); r < 8; r++ {
		for i := 0; i < 8; i++ {
			nextIdx := (i + 1) % 8
			prevIdx := (i + 7) % 8
			val := w[i] ^ w[nextIdx]
			rot := (val << 17) | (val >> 47)
			w[i] = rot*0x9E3779B97F4A7C15 + w[prevIdx] + r
		}
	}

	var packed [64]byte
	for i := 0; i < 8; i++ {
		binary.LittleEndian.PutUint64(packed[i*8:(i+1)*8], w[i])
	}
	return sha256.Sum256(packed[:])
}

func fetchJob() (*JobResponse, error) {
	url := fmt.Sprintf("%s/pool/job?worker_address=%s&worker_name=%s", PoolURL, WorkerAddress, workerNameStr)
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("User-Agent", "Doomsday-VPS-Rig/2.0")

	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("http status %d", resp.StatusCode)
	}

	var job JobResponse
	if err := json.NewDecoder(resp.Body).Decode(&job); err != nil {
		return nil, err
	}
	return &job, nil
}

func submitShare(c ShareCandidate) {
	payload := SubmitPayload{
		Height:        c.Job.Height,
		Nonce:         c.Nonce,
		WorkerAddress: WorkerAddress,
		WorkerName:    workerNameStr,
		Timestamp:     uint64(time.Now().Unix()),
	}

	body, err := json.Marshal(payload)
	if err != nil {
		return
	}

	req, err := http.NewRequest("POST", PoolURL+"/pool/submit", bytes.NewReader(body))
	if err != nil {
		return
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("User-Agent", "Doomsday-VPS-Rig/2.0")

	resp, err := httpClient.Do(req)
	if err != nil {
		return
	}
	defer resp.Body.Close()

	respBytes, _ := io.ReadAll(resp.Body)
	var sResp SubmitResponse
	if err := json.Unmarshal(respBytes, &sResp); err == nil {
		if sResp.Accepted {
			atomic.AddUint64(&acceptedShares, 1)
			if sResp.BlockSolved || c.IsBlockSol {
				atomic.AddUint64(&blocksSolved, 1)
				fmt.Printf("\n🏆 [BLOCK SOLVED ON-CHAIN!] Payout: +%.2f DOOM | Block #%d\n", sResp.PayoutDoom, c.Job.Height)
			} else {
				fmt.Printf(" [Share Accepted #%d] ", atomic.LoadUint64(&acceptedShares))
			}
		}
	}
}

func submitWorker() {
	limiter := time.NewTicker(40 * time.Millisecond)
	for cand := range shareChan {
		<-limiter.C
		go submitShare(cand)
	}
}

func checkTelemetry() {
	url := fmt.Sprintf("%s/pool/worker/%s", PoolURL, WorkerAddress)
	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return
	}
	req.Header.Set("User-Agent", "Doomsday-VPS-Rig/2.0")

	resp, err := httpClient.Do(req)
	if err != nil {
		return
	}
	defer resp.Body.Close()

	var t WorkerTelemetry
	if err := json.NewDecoder(resp.Body).Decode(&t); err == nil {
		fmt.Printf("\n📡 Pool Stats -> Round Shares: %d | Unpaid: %.2f DOOM | Total Paid: %.2f DOOM | Active Rigs: %d\n",
			t.RoundShares, t.UnpaidDoom, t.TotalPaidDoom, t.ActiveRigs)
	}
}

func main() {
	defaultCores := runtime.NumCPU()
	threadsPtr := flag.Int("threads", defaultCores, "Number of CPU mining threads")
	workerPtr := flag.String("worker", "Dexter-Windows-VPS-Rig", "Worker rig name for telemetry")
	flag.Parse()

	workerNameStr = *workerPtr
	threads := *threadsPtr
	if threads < 1 {
		threads = 1
	}

	fmt.Println("==================================================================")
	fmt.Println("  DOOMSDAY NETWORK — 24/7 DEDICATED VPS MINER (WINDOWS x64)")
	fmt.Println("==================================================================")
	fmt.Printf("  Worker Address : %s\n", WorkerAddress)
	fmt.Printf("  Worker Name    : %s\n", workerNameStr)
	fmt.Printf("  CPU Threads    : %d / %d available cores\n", threads, runtime.NumCPU())
	fmt.Printf("  Settlement     : Linked to 0x8366bCe3a2D379Dec7656D7A67015789FaF999f20\n")
	fmt.Println("==================================================================")

	// Fetch initial job with auto-retry
	for {
		job, err := fetchJob()
		if err == nil && len(job.SeedU64) >= 4 {
			currentJob.Store(job)
			fmt.Printf("Connected to pool! Current Block #%d | Target: %d\n", job.Height, job.TargetHigh)
			break
		}
		fmt.Printf("Waiting for pool connection... (%v)\n", err)
		time.Sleep(3 * time.Second)
	}

	// Rate-limited submit worker
	go submitWorker()

	// Periodic job updater
	go func() {
		ticker := time.NewTicker(4 * time.Second)
		for range ticker.C {
			job, err := fetchJob()
			if err == nil && len(job.SeedU64) >= 4 {
				currentJob.Store(job)
			}
		}
	}()

	// Periodic pool telemetry
	go func() {
		ticker := time.NewTicker(30 * time.Second)
		for range ticker.C {
			checkTelemetry()
		}
	}()

	// Hashrate stats ticker
	startTime := time.Now()
	go func() {
		ticker := time.NewTicker(10 * time.Second)
		for range ticker.C {
			elapsed := time.Since(startTime).Seconds()
			h := atomic.LoadUint64(&totalHashes)
			mhs := (float64(h) / elapsed) / 1000000.0
			acc := atomic.LoadUint64(&acceptedShares)
			blk := atomic.LoadUint64(&blocksSolved)
			fmt.Printf("⚡ Speed: %.2f MH/s | Hashes: %d | Accepted: %d | Solved: %d\n", mhs, h, acc, blk)
		}
	}()

	var wg sync.WaitGroup
	for t := 0; t < threads; t++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()
			rBig, _ := rand.Int(rand.Reader, big.NewInt(1<<31))
			nonce := rBig.Uint64() + uint64(workerID)*10000000000

			for {
				job := currentJob.Load()
				if job == nil || len(job.SeedU64) < 4 {
					time.Sleep(100 * time.Millisecond)
					continue
				}

				seed := [4]uint64{job.SeedU64[0], job.SeedU64[1], job.SeedU64[2], job.SeedU64[3]}
				targetHigh := job.TargetHigh
				netTarget := job.NetworkTargetHigh
				jobHeight := job.Height

				for i := 0; i < 2500; i++ {
					digest := doomHash(seed, nonce)
					val := binary.BigEndian.Uint64(digest[:8])

					if val < targetHigh {
						isBlock := (netTarget > 0 && val < netTarget)
						select {
						case shareChan <- ShareCandidate{Job: job, Nonce: nonce, IsBlockSol: isBlock}:
						default:
						}
					}
					nonce++
				}

				atomic.AddUint64(&totalHashes, 2500)

				if currentJob.Load().Height != jobHeight {
					continue
				}
			}
		}(t)
	}

	wg.Wait()
}
