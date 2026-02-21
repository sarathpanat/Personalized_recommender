#!/bin/sh
set -e

DATA_FILE="/app/data/sample_data.csv"

if [ ! -f "$DATA_FILE" ]; then
  echo "⏳ sample_data.csv not found. Running llm_gen.py to generate dataset..."
  python data/llm_gen.py
  echo "✅ Dataset generated successfully."
else
  echo "✅ sample_data.csv already exists. Skipping data generation."
fi
