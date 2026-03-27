---
name: analyze-results
description: Analyze results.tsv to summarize experiment history, best runs, and suggest next experiments
---

You are analyzing the CV_AgenticTune experiment history. Do the following:

1. **Read `results.tsv`**
   - Parse all columns: run_id, change_description, map50_95, peak_vram_mb, status

2. **Summarize**
   - Total runs, kept vs reverted
   - Best run: lowest mAP 50-95 achieved and what change produced it
   - VRAM trend: any runs that caused significant VRAM increase

3. **Identify patterns**
   - Which types of changes tend to help (augmentation, LR, architecture, etc.)
   - Which directions consistently fail

4. **Suggest next 3 experiments**
   - Ranked by expected impact
   - Each suggestion should be a single focused change
   - Prefer changes not yet tried, or variations on what worked

Present the analysis as a clear, concise report.
