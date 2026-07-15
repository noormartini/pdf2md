# PDF-to-Markdown Conversion Experiment Report

**Total evaluations:** 360
**Errors:** 0 (0.0%)

## Strategy Comparison

| Strategy | Pages | Avg Time (ms) | text_similarity | heading_structure | list_structure | table_structure | code_block_score | paragraph_structure | word_overlap |
| -------- | ----- | ------------- | --------------- | ----------------- | -------------- | --------------- | ---------------- | ------------------- | ------------ |
| adaptive | 90    | 20790.1       | 0.838           | 0.542             | 0.868          | 0.956           | 0.752            | 0.636               | 0.794        |
| hybrid   | 90    | 68009.5       | 0.818           | 0.348             | 0.891          | 0.944           | 0.736            | 0.597               | 0.795        |
| image    | 90    | 64696.3       | 0.827           | 0.429             | 0.914          | 0.944           | 0.250            | 0.156               | 0.811        |
| text     | 90    | 197.3         | 0.860           | 0.565             | 0.859          | 0.922           | 0.889            | 0.726               | 0.761        |

## Model Comparison

| Model                              | Pages | Avg Time (ms) | text_similarity | heading_structure | list_structure | table_structure | code_block_score | paragraph_structure | word_overlap |
| ---------------------------------- | ----- | ------------- | --------------- | ----------------- | -------------- | --------------- | ---------------- | ------------------- | ------------ |
| qwen2.5-vl-7b-instruct-abliterated | 360   | 38423.3       | 0.836           | 0.471             | 0.883          | 0.942           | 0.657            | 0.529               | 0.790        |

## Strategy × Model Matrix (Text Similarity)

| Strategy | qwen2.5-vl-7b-instruct-abliterated |
| -------- | :--------------------------------: |
| adaptive |            0.838 (n=90)            |
| hybrid   |            0.818 (n=90)            |
| image    |            0.827 (n=90)            |
| text     |            0.860 (n=90)            |

## Results by Document Category

| Category |   adaptive   |    hybrid    |    image     |     text     |
| -------- | :----------: | :----------: | :----------: | :----------: |
| academic | 0.838 (n=90) | 0.818 (n=90) | 0.827 (n=90) | 0.860 (n=90) |

## Per-Page Breakdown

| Page | Best Strategy | Best Model                         | Best Similarity | Worst Error |
| ---- | ------------- | ---------------------------------- | --------------- | ----------- |
| 1    | text          | qwen2.5-vl-7b-instruct-abliterated | 0.993           | -           |
| 2    | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.992           | -           |
| 3    | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.996           | -           |
| 4    | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.997           | -           |
| 5    | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.997           | -           |
| 6    | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.728           | -           |
| 7    | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.999           | -           |
| 8    | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.991           | -           |
| 9    | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.964           | -           |
| 10   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.995           | -           |
| 11   | image         | qwen2.5-vl-7b-instruct-abliterated | 0.989           | -           |
| 12   | image         | qwen2.5-vl-7b-instruct-abliterated | 0.988           | -           |
| 13   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.997           | -           |
| 14   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.993           | -           |
| 15   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.997           | -           |
| 16   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.995           | -           |
| 17   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.991           | -           |
| 18   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.999           | -           |
| 19   | image         | qwen2.5-vl-7b-instruct-abliterated | 0.988           | -           |
| 20   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.967           | -           |
| 21   | image         | qwen2.5-vl-7b-instruct-abliterated | 0.990           | -           |
| 22   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.991           | -           |
| 23   | image         | qwen2.5-vl-7b-instruct-abliterated | 0.995           | -           |
| 24   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.996           | -           |
| 25   | image         | qwen2.5-vl-7b-instruct-abliterated | 0.984           | -           |
| 26   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.984           | -           |
| 27   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.993           | -           |
| 28   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.985           | -           |
| 29   | text          | qwen2.5-vl-7b-instruct-abliterated | 0.976           | -           |
| 30   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.991           | -           |

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
