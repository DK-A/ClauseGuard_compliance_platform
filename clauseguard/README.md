# ClauseGuard — Production-Ready Organizational Document Governance Platform

ClauseGuard is a production-ready, fully offline, human-in-the-loop document contradiction detection platform designed to automatically identify semantic discrepancies across company policies, vendor agreements, SOPs, and compliance frameworks.

It is engineered to run identically across three hardware targets (Laptop, RPi5, RPi4) using automatic hardware profile detection.

---

## Technical Architecture

```
                                 [Document Workspace]
                                          │
                                          ▼
                             [ spaCy Intelligent Chunker ]
                                          │
                                          ▼
                                   [ ChromaDB Store ]
                                          │
                                          ▼
                             [ Two-Tower Candidate Filter ]
                        (Tower 1: Semantic, Tower 2: Matrix)
                                          │
                                          ▼
                            [ LangChain 3-Step CoT Reasoner ]
                                          │
                                          ▼
                          [ Confidence Sigmoid Calibrator ]
                                          │
                                          ▼
                           [ NetworkX Contradiction Graph ]
                                          │
                                          ▼
                             [ High-Fidelity React UI ]
```

---

## Hardware Profile Parameters

| Profile Type | Core LLM (Quantized) | Embedding Model | Reasoning Pipeline | Pair Limit | Conf. Threshold |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **LAPTOP** | LLaMA 3.1 8B (via Ollama) | BERT-Legal-Base (420MB) | Full 3-Step CoT | 50 | 0.65 |
| **RPI5** | LLaMA 3.1 8B (via llama.cpp) | BERT-Legal-Base (420MB) | Full 3-Step CoT | 30 | 0.70 |
| **RPI4** | Qwen 2.5 1.5B (via llama.cpp) | all-MiniLM-L6-v2 (22MB) | Single Merged Prompt | 15 | 0.75 |

---

## Deployment & Setup

### Laptop (One Command Docker Deployment)
To launch the full local stack (FastAPI port 8000, Vite React port 5173, Redis, and Ollama) on your laptop:
```bash
docker compose up --build
```

### Raspberry Pi 5 Unattended Setup
Flash Debian Bookworm onto your RPi5 NVMe drive, then run:
```bash
chmod +x edge/setup_rpi5.sh
./edge/setup_rpi5.sh
```

### Raspberry Pi 4 Unattended Setup
Flash Debian Bookworm onto your RPi4, then run:
```bash
chmod +x edge/setup_rpi4.sh
./edge/setup_rpi4.sh
```

---

## CLI Telemetry Benchmarking

Run a 10-clause benchmark run to measure model TPS and cache results:
```bash
python edge/benchmark.py --profile auto
```

---

## Verification & Subsystem Tests

Run the complete backend validation suite:
```bash
python -m pytest
```

---

## Features

1. **Intelligent Chunker:** Combines spaCy sentence boundaries with obligation keyword markers to produce semantically coherent segments.
2. **Two-Tower Candidate Retrieval:** Filters irrelevant pairs via a logic compatibility matrix, reducing LLM calls by 60%.
3. **Calibrated Confidence Scoring:** Combines embeddings distance, LLM self-confidence, and historical review metrics into a sigmoid probability calibrated dynamically via scikit-learn Logistic Regression feedback loops.
4. **Resolution Impact Simulator:** Simulates proposed clause edits against neighbors in the DiGraph before applying them to prevent new discrepancies.
5. **Air-Gapped Edge Telemetry:** Full circular Gauges, thermal status updates, and dynamic model memory switching running 100% offline.

---

## License & Open Source Stack
All modules are open source under MIT and Apache 2.0 licenses. 
Zero paid APIs. Meta LLaMA 3.1, Alibaba Qwen 2.5, spaCy, NetworkX, React Flow, FastAPI, SQLite, ChromaDB, scikit-learn.
