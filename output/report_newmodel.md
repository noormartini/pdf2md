# PDF-to-Markdown Conversion Experiment Report

**Total evaluations:** 360
**Errors:** 0 (0.0%)

## Strategy Comparison

| Strategy | Pages | Avg Time (ms) | text_similarity | heading_structure | list_structure | table_structure | code_block_score | paragraph_structure | word_overlap |
| -------- | ----- | ------------- | --------------- | ----------------- | -------------- | --------------- | ---------------- | ------------------- | ------------ |
| adaptive | 90    | 1671.5        | 0.884           | 0.534             | 0.848          | 0.933           | 0.900            | 0.711               | 0.827        |
| hybrid   | 90    | 9919.8        | 0.806           | 0.485             | 0.920          | 0.933           | 0.989            | 0.749               | 0.784        |
| image    | 90    | 7274.9        | 0.839           | 0.438             | 0.878          | 0.933           | 1.000            | 0.745               | 0.810        |
| text     | 90    | 156.7         | 0.860           | 0.564             | 0.859          | 0.922           | 0.889            | 0.726               | 0.761        |

## Model Comparison

| Model                | Pages | Avg Time (ms) | text_similarity | heading_structure | list_structure | table_structure | code_block_score | paragraph_structure | word_overlap |
| -------------------- | ----- | ------------- | --------------- | ----------------- | -------------- | --------------- | ---------------- | ------------------- | ------------ |
| qwen/qwen3.6-35b-a3b | 360   | 4755.7        | 0.847           | 0.505             | 0.876          | 0.931           | 0.944            | 0.733               | 0.795        |

## Strategy × Model Matrix (Text Similarity)

| Strategy | qwen/qwen3.6-35b-a3b |
| -------- | :------------------: |
| adaptive |     0.884 (n=90)     |
| hybrid   |     0.806 (n=90)     |
| image    |     0.839 (n=90)     |
| text     |     0.860 (n=90)     |

## Results by Document Category

| Category |   adaptive   |    hybrid    |    image     |     text     |
| -------- | :----------: | :----------: | :----------: | :----------: |
| academic | 0.884 (n=90) | 0.806 (n=90) | 0.839 (n=90) | 0.860 (n=90) |

## Per-Page Breakdown

| Page | Best Strategy | Best Model           | Best Similarity | Worst Error |
| ---- | ------------- | -------------------- | --------------- | ----------- |
| 1    | text          | qwen/qwen3.6-35b-a3b | 0.993           | -           |
| 2    | adaptive      | qwen/qwen3.6-35b-a3b | 0.992           | -           |
| 3    | image         | qwen/qwen3.6-35b-a3b | 0.999           | -           |
| 4    | image         | qwen/qwen3.6-35b-a3b | 0.998           | -           |
| 5    | hybrid        | qwen/qwen3.6-35b-a3b | 0.998           | -           |
| 6    | adaptive      | qwen/qwen3.6-35b-a3b | 0.861           | -           |
| 7    | hybrid        | qwen/qwen3.6-35b-a3b | 0.998           | -           |
| 8    | image         | qwen/qwen3.6-35b-a3b | 0.991           | -           |
| 9    | hybrid        | qwen/qwen3.6-35b-a3b | 0.991           | -           |
| 10   | adaptive      | qwen/qwen3.6-35b-a3b | 0.995           | -           |
| 11   | hybrid        | qwen/qwen3.6-35b-a3b | 0.982           | -           |
| 12   | hybrid        | qwen/qwen3.6-35b-a3b | 0.993           | -           |
| 13   | image         | qwen/qwen3.6-35b-a3b | 0.999           | -           |
| 14   | image         | qwen/qwen3.6-35b-a3b | 0.994           | -           |
| 15   | hybrid        | qwen/qwen3.6-35b-a3b | 0.997           | -           |
| 16   | image         | qwen/qwen3.6-35b-a3b | 0.995           | -           |
| 17   | image         | qwen/qwen3.6-35b-a3b | 0.993           | -           |
| 18   | hybrid        | qwen/qwen3.6-35b-a3b | 0.998           | -           |
| 19   | hybrid        | qwen/qwen3.6-35b-a3b | 0.997           | -           |
| 20   | image         | qwen/qwen3.6-35b-a3b | 0.998           | -           |
| 21   | image         | qwen/qwen3.6-35b-a3b | 0.997           | -           |
| 22   | image         | qwen/qwen3.6-35b-a3b | 0.996           | -           |
| 23   | image         | qwen/qwen3.6-35b-a3b | 0.995           | -           |
| 24   | adaptive      | qwen/qwen3.6-35b-a3b | 0.996           | -           |
| 25   | hybrid        | qwen/qwen3.6-35b-a3b | 0.998           | -           |
| 26   | image         | qwen/qwen3.6-35b-a3b | 0.989           | -           |
| 27   | image         | qwen/qwen3.6-35b-a3b | 0.997           | -           |
| 28   | image         | qwen/qwen3.6-35b-a3b | 0.982           | -           |
| 29   | image         | qwen/qwen3.6-35b-a3b | 0.990           | -           |
| 30   | adaptive      | qwen/qwen3.6-35b-a3b | 0.991           | -           |

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
