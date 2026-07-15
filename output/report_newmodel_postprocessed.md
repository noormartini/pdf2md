# PDF-to-Markdown Conversion Experiment Report

**Total evaluations:** 360
**Errors:** 0 (0.0%)

## Strategy Comparison

| Strategy | Pages | Avg Time (ms) | text_similarity | heading_structure | list_structure | table_structure | code_block_score | paragraph_structure | word_overlap |
| -------- | ----- | ------------- | --------------- | ----------------- | -------------- | --------------- | ---------------- | ------------------- | ------------ |
| adaptive | 90    | 1699.0        | 0.907           | 0.816             | 0.904          | 0.944           | 0.989            | 0.815               | 0.865        |
| hybrid   | 90    | 9884.8        | 0.809           | 0.747             | 0.920          | 0.933           | 0.967            | 0.803               | 0.791        |
| image    | 90    | 7269.5        | 0.837           | 0.826             | 0.878          | 0.933           | 0.978            | 0.815               | 0.821        |
| text     | 90    | 155.2         | 0.893           | 0.808             | 0.904          | 0.933           | 1.000            | 0.815               | 0.804        |

## Model Comparison

| Model                | Pages | Avg Time (ms) | text_similarity | heading_structure | list_structure | table_structure | code_block_score | paragraph_structure | word_overlap |
| -------------------- | ----- | ------------- | --------------- | ----------------- | -------------- | --------------- | ---------------- | ------------------- | ------------ |
| qwen/qwen3.6-35b-a3b | 360   | 4752.1        | 0.862           | 0.799             | 0.901          | 0.936           | 0.983            | 0.812               | 0.820        |

## Strategy × Model Matrix (Text Similarity)

| Strategy | qwen/qwen3.6-35b-a3b |
| -------- | :------------------: |
| adaptive |     0.907 (n=90)     |
| hybrid   |     0.809 (n=90)     |
| image    |     0.837 (n=90)     |
| text     |     0.893 (n=90)     |

## Results by Document Category

| Category |   adaptive   |    hybrid    |    image     |     text     |
| -------- | :----------: | :----------: | :----------: | :----------: |
| academic | 0.907 (n=90) | 0.809 (n=90) | 0.837 (n=90) | 0.893 (n=90) |

## Per-Page Breakdown

| Page | Best Strategy | Best Model           | Best Similarity | Worst Error |
| ---- | ------------- | -------------------- | --------------- | ----------- |
| 1    | text          | qwen/qwen3.6-35b-a3b | 0.972           | -           |
| 2    | adaptive      | qwen/qwen3.6-35b-a3b | 0.987           | -           |
| 3    | text          | qwen/qwen3.6-35b-a3b | 0.996           | -           |
| 4    | image         | qwen/qwen3.6-35b-a3b | 0.998           | -           |
| 5    | image         | qwen/qwen3.6-35b-a3b | 0.998           | -           |
| 6    | adaptive      | qwen/qwen3.6-35b-a3b | 0.868           | -           |
| 7    | adaptive      | qwen/qwen3.6-35b-a3b | 0.999           | -           |
| 8    | image         | qwen/qwen3.6-35b-a3b | 0.998           | -           |
| 9    | text          | qwen/qwen3.6-35b-a3b | 0.997           | -           |
| 10   | adaptive      | qwen/qwen3.6-35b-a3b | 0.999           | -           |
| 11   | image         | qwen/qwen3.6-35b-a3b | 0.999           | -           |
| 12   | adaptive      | qwen/qwen3.6-35b-a3b | 0.998           | -           |
| 13   | image         | qwen/qwen3.6-35b-a3b | 0.999           | -           |
| 14   | image         | qwen/qwen3.6-35b-a3b | 0.999           | -           |
| 15   | hybrid        | qwen/qwen3.6-35b-a3b | 0.998           | -           |
| 16   | adaptive      | qwen/qwen3.6-35b-a3b | 0.999           | -           |
| 17   | adaptive      | qwen/qwen3.6-35b-a3b | 0.999           | -           |
| 18   | adaptive      | qwen/qwen3.6-35b-a3b | 0.999           | -           |
| 19   | adaptive      | qwen/qwen3.6-35b-a3b | 0.998           | -           |
| 20   | image         | qwen/qwen3.6-35b-a3b | 0.999           | -           |
| 21   | image         | qwen/qwen3.6-35b-a3b | 0.999           | -           |
| 22   | image         | qwen/qwen3.6-35b-a3b | 0.999           | -           |
| 23   | image         | qwen/qwen3.6-35b-a3b | 0.999           | -           |
| 24   | adaptive      | qwen/qwen3.6-35b-a3b | 0.999           | -           |
| 25   | image         | qwen/qwen3.6-35b-a3b | 0.998           | -           |
| 26   | adaptive      | qwen/qwen3.6-35b-a3b | 0.998           | -           |
| 27   | image         | qwen/qwen3.6-35b-a3b | 0.999           | -           |
| 28   | adaptive      | qwen/qwen3.6-35b-a3b | 0.984           | -           |
| 29   | image         | qwen/qwen3.6-35b-a3b | 0.996           | -           |
| 30   | image         | qwen/qwen3.6-35b-a3b | 0.997           | -           |

## Metric Definitions


| Metric | Description |
|--------|-------------|
| text_similarity | SequenceMatcher ratio (0-1) comparing normalized text |
| heading_structure | Similarity of heading counts by level (H1-H6) |
| list_structure | Similarity of bullet and numbered list counts |
| table_structure | Similarity of table separator counts |
| code_block_score | Similarity of fenced code block counts |
| paragraph_structure | Similarity of paragraph counts (with 20% tolerance) |
| word_overlap | Jaccard similarity of word sets |
