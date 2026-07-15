# PDF-to-Markdown Conversion Experiment Report

**Total evaluations:** 360
**Errors:** 0 (0.0%)

## Strategy Comparison

| Strategy | Pages | Avg Time (ms) | text_similarity | heading_structure | list_structure | table_structure | code_block_score | paragraph_structure | word_overlap |
| -------- | ----- | ------------- | --------------- | ----------------- | -------------- | --------------- | ---------------- | ------------------- | ------------ |
| adaptive | 90    | 704.5         | 0.894           | 0.803             | 0.919          | 0.978           | 0.994            | 0.808               | 0.854        |
| hybrid   | 90    | 3170.2        | 0.813           | 0.523             | 0.875          | 0.944           | 0.946            | 0.774               | 0.835        |
| image    | 90    | 3250.2        | 0.839           | 0.685             | 0.911          | 0.944           | 0.972            | 0.782               | 0.838        |
| text     | 90    | 153.7         | 0.893           | 0.808             | 0.904          | 0.933           | 1.000            | 0.815               | 0.804        |

## Model Comparison

| Model                              | Pages | Avg Time (ms) | text_similarity | heading_structure | list_structure | table_structure | code_block_score | paragraph_structure | word_overlap |
| ---------------------------------- | ----- | ------------- | --------------- | ----------------- | -------------- | --------------- | ---------------- | ------------------- | ------------ |
| qwen2.5-vl-7b-instruct-abliterated | 360   | 1819.6        | 0.860           | 0.705             | 0.902          | 0.950           | 0.978            | 0.795               | 0.833        |

## Strategy × Model Matrix (Text Similarity)

| Strategy | qwen2.5-vl-7b-instruct-abliterated |
| -------- | :--------------------------------: |
| adaptive |            0.894 (n=90)            |
| hybrid   |            0.813 (n=90)            |
| image    |            0.839 (n=90)            |
| text     |            0.893 (n=90)            |

## Results by Document Category

| Category |   adaptive   |    hybrid    |    image     |     text     |
| -------- | :----------: | :----------: | :----------: | :----------: |
| academic | 0.894 (n=90) | 0.813 (n=90) | 0.839 (n=90) | 0.893 (n=90) |

## Per-Page Breakdown

| Page | Best Strategy | Best Model                         | Best Similarity | Worst Error |
| ---- | ------------- | ---------------------------------- | --------------- | ----------- |
| 1    | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.976           | -           |
| 2    | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.987           | -           |
| 3    | text          | qwen2.5-vl-7b-instruct-abliterated | 0.996           | -           |
| 4    | image         | qwen2.5-vl-7b-instruct-abliterated | 0.998           | -           |
| 5    | image         | qwen2.5-vl-7b-instruct-abliterated | 0.998           | -           |
| 6    | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.917           | -           |
| 7    | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.999           | -           |
| 8    | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.998           | -           |
| 9    | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.999           | -           |
| 10   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.999           | -           |
| 11   | image         | qwen2.5-vl-7b-instruct-abliterated | 0.998           | -           |
| 12   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.998           | -           |
| 13   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.999           | -           |
| 14   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.998           | -           |
| 15   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.996           | -           |
| 16   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.999           | -           |
| 17   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.999           | -           |
| 18   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.999           | -           |
| 19   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.998           | -           |
| 20   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.997           | -           |
| 21   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.994           | -           |
| 22   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.996           | -           |
| 23   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.999           | -           |
| 24   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.999           | -           |
| 25   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.995           | -           |
| 26   | image         | qwen2.5-vl-7b-instruct-abliterated | 0.994           | -           |
| 27   | text          | qwen2.5-vl-7b-instruct-abliterated | 0.999           | -           |
| 28   | image         | qwen2.5-vl-7b-instruct-abliterated | 0.991           | -           |
| 29   | text          | qwen2.5-vl-7b-instruct-abliterated | 0.996           | -           |
| 30   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.997           | -           |

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
