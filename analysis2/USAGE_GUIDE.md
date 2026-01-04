# Analysis Script Usage Guide

## Overview

The analysis script now supports **modular execution**, allowing you to run specific steps instead of the entire pipeline. This saves time and API costs when you only need to update certain parts of the analysis.

## Quick Start

### Run All Steps (Default)
```bash
python -m analysis2.analyze
```

### Run Specific Steps
```bash
# Re-run only Sales Evaluation
python -m analysis2.analyze --steps 10

# Re-run Sales Evaluation, Critique, and Executive Summary
python -m analysis2.analyze --steps 10 11 13

# Re-run from Speaking Time Analysis onwards
python -m analysis2.analyze --from 9
```

### List Available Steps
```bash
python -m analysis2.analyze --list
```

### Clear Cache and Start Fresh
```bash
python -m analysis2.analyze --clear
```

## Step Reference

| Step | Name | Description | Dependencies |
|------|------|-------------|--------------|
| 0 | Speaker Identification | Identifies Customer vs Technician | None |
| 1 | Location & Context | Extracts location info | Step 0 |
| 2 | Pricing Extraction | Finds pricing mentions | Step 0 |
| 3 | Overall Summary | Generates call summary | Step 0 |
| 4 | Compliance Analysis | Analyzes compliance questions | Step 0 |
| 5 | Structured Analysis | Extracts client situation & products | Step 0 |
| 6 | Customer Objections | Analyzes objections & concerns | Step 0 |
| 7 | Product Interest | Analyzes interest in products | Steps 0, 5 |
| 8 | Perplexity Research | External product research | Steps 0, 1, 5, 7 |
| 9 | Speaking Time Analysis | Calculates 70/30 ratio | Step 0 |
| 10 | **Sales Evaluation** | 4 sales questions analysis | Steps 0, 5, 6, 7, 9 |
| 11 | Technician Critique | Overall performance critique | Steps 4, 7, 10 |
| 12 | Product Comparison | Picks winner product | Steps 0, 7, 8 |
| 13 | Executive Summary | Generates final summary | All steps |

## Common Use Cases

### 1. Fix Speaking Time Bug and Re-run Sales Evaluation
```bash
# After fixing the calculate_speaking_time_ratio bug
python -m analysis2.analyze --steps 9 10 11 13
```
This will:
- Recalculate speaking time (step 9)
- Re-run sales evaluation with correct data (step 10)
- Update technician critique (step 11)
- Regenerate executive summary (step 13)

### 2. Update Only Sales Questions
```bash
python -m analysis2.analyze --steps 10 11 13
```
This re-runs sales evaluation, critique, and summary without touching other steps.

### 3. Re-run Everything from Compliance Onwards
```bash
python -m analysis2.analyze --from 4
```

### 4. Test a Single Step
```bash
python -m analysis2.analyze --steps 10
```
Note: Make sure dependencies have been run previously!

## How It Works

### Checkpoints
- Each step saves a checkpoint in `data/.analysis_cache/`
- When you run specific steps, existing steps load from:
  1. Current results file (`comprehensive_analysis.json`)
  2. Checkpoint cache
  3. Re-computation if neither exists

### Dependencies
The script automatically loads dependencies from existing data:
- Steps that need previous data will load from `comprehensive_analysis.json`
- Missing dependencies will be loaded from checkpoints or computed if needed

### Cache Management
- `--clear`: Clears all checkpoints (forces full recomputation)
- Checkpoints are preserved when running partial steps
- Checkpoints are cleared only when all 14 steps complete successfully

## Tips

1. **After Code Changes**: Run only affected steps
   ```bash
   python -m analysis2.analyze --steps 10 11 13
   ```

2. **Debugging**: Run single steps to isolate issues
   ```bash
   python -m analysis2.analyze --steps 10
   ```

3. **Fresh Start**: Clear cache periodically
   ```bash
   python -m analysis2.analyze --clear
   ```

4. **Check Results**: Always include step 13 (Executive Summary) when updating multiple steps
   ```bash
   python -m analysis2.analyze --steps 10 11 13
   ```

## Cost Savings

Running specific steps significantly reduces API costs:
- Full run: ~$1-2 (all GPT-4o + Perplexity calls)
- Sales Evaluation only (step 10): ~$0.20 (4 GPT-4o calls)
- Update critique & summary (steps 11, 13): ~$0.10 (2 GPT-4o calls)

## Troubleshooting

### "Missing dependency" errors
If you get errors about missing data, run the dependency steps first:
```bash
# If step 10 fails due to missing products
python -m analysis2.analyze --steps 5 7 10 11 13
```

### Cache issues
Clear cache and try again:
```bash
python -m analysis2.analyze --clear --steps 10
```

### Verify what's cached
Check `data/.analysis_cache/` for checkpoint files:
```bash
ls -la data/.analysis_cache/
```

## Examples

### Scenario: Fixed the speaking time calculation bug
```bash
# Step 1: Re-run speaking time analysis
python -m analysis2.analyze --steps 9

# Step 2: Re-run sales evaluation (uses new speaking time data)
python -m analysis2.analyze --steps 10

# Step 3: Update dependent steps
python -m analysis2.analyze --steps 11 13
```

Or all at once:
```bash
python -m analysis2.analyze --steps 9 10 11 13
```

### Scenario: Changed sales evaluation questions
```bash
python -m analysis2.analyze --steps 10 11 13
```

### Scenario: Updated product analysis logic
```bash
python -m analysis2.analyze --from 7
```

## Architecture

```
Load existing results (if partial run)
  ↓
For each step in steps_to_run:
  ↓
  Check cache → Run analysis → Save checkpoint
  ↓
Save comprehensive_analysis.json
```

This modular approach lets you iterate quickly on specific features without waiting for the entire pipeline to complete!

