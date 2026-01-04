#!/bin/bash
# Run the comprehensive analysis script

echo "================================"
echo "Service Call Analysis - Step 2"
echo "================================"
echo ""
echo "This script will analyze the service call transcript"
echo "and generate comprehensive_analysis.json"
echo ""

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Make sure you have set OPENAI_API_KEY environment variable"
    echo ""
fi

# Check if transcript exists
if [ ! -f "../data/transcription.json" ]; then
    echo "❌ Error: transcription.json not found in data/"
    echo "Please run the transcription first"
    exit 1
fi

echo "✓ Transcript found"
echo "✓ Starting analysis..."
echo ""

# Run the analysis
python analyze.py

if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "✓ Analysis complete!"
    echo "================================"
    echo ""
    echo "Next steps:"
    echo "1. View the analysis: cat ../data/comprehensive_analysis.json | jq"
    echo "2. Run the web app: cd .. && python run_webapp.py 2"
    echo ""
else
    echo ""
    echo "❌ Analysis failed. Check the error messages above."
    exit 1
fi

