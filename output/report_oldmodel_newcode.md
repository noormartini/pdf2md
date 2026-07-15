# PDF-to-Markdown Conversion Experiment Report

**Total evaluations:** 360
**Errors:** 0 (0.0%)

## Strategy Comparison

| Strategy | Pages | Avg Time (ms) | text_similarity | heading_structure | list_structure | table_structure | code_block_score | paragraph_structure | word_overlap |
| -------- | ----- | ------------- | --------------- | ----------------- | -------------- | --------------- | ---------------- | ------------------- | ------------ |
| adaptive | 90    | 1730.3        | 0.874           | 0.574             | 0.848          | 0.944           | 0.652            | 0.552               | 0.819        |
| hybrid   | 90    | 3141.2        | 0.838           | 0.419             | 0.875          | 0.944           | 0.544            | 0.407               | 0.826        |
| image    | 90    | 6265.2        | 0.832           | 0.429             | 0.911          | 0.944           | 0.076            | 0.065               | 0.822        |
| text     | 90    | 158.3         | 0.860           | 0.564             | 0.859          | 0.922           | 0.889            | 0.726               | 0.761        |

## Model Comparison

| Model                              | Pages | Avg Time (ms) | text_similarity | heading_structure | list_structure | table_structure | code_block_score | paragraph_structure | word_overlap |
| ---------------------------------- | ----- | ------------- | --------------- | ----------------- | -------------- | --------------- | ---------------- | ------------------- | ------------ |
| qwen2.5-vl-7b-instruct-abliterated | 360   | 2823.7        | 0.851           | 0.497             | 0.873          | 0.939           | 0.540            | 0.438               | 0.807        |

## Strategy × Model Matrix (Text Similarity)

| Strategy | qwen2.5-vl-7b-instruct-abliterated |
| -------- | :--------------------------------: |
| adaptive |            0.874 (n=90)            |
| hybrid   |            0.838 (n=90)            |
| image    |            0.832 (n=90)            |
| text     |            0.860 (n=90)            |

## Results by Document Category

| Category |   adaptive   |    hybrid    |    image     |     text     |
| -------- | :----------: | :----------: | :----------: | :----------: |
| academic | 0.874 (n=90) | 0.838 (n=90) | 0.832 (n=90) | 0.860 (n=90) |

## Per-Page Breakdown

| Page | Best Strategy | Best Model                         | Best Similarity | Worst Error |
| ---- | ------------- | ---------------------------------- | --------------- | ----------- |
| 1    | text          | qwen2.5-vl-7b-instruct-abliterated | 0.993           | -           |
| 2    | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.992           | -           |
| 3    | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.997           | -           |
| 4    | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.997           | -           |
| 5    | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.997           | -           |
| 6    | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.688           | -           |
| 7    | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.999           | -           |
| 8    | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.989           | -           |
| 9    | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.966           | -           |
| 10   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.995           | -           |
| 11   | image         | qwen2.5-vl-7b-instruct-abliterated | 0.995           | -           |
| 12   | image         | qwen2.5-vl-7b-instruct-abliterated | 0.989           | -           |
| 13   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.998           | -           |
| 14   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.993           | -           |
| 15   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.997           | -           |
| 16   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.995           | -           |
| 17   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.991           | -           |
| 18   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.995           | -           |
| 19   | image         | qwen2.5-vl-7b-instruct-abliterated | 0.988           | -           |
| 20   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.967           | -           |
| 21   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.994           | -           |
| 22   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.991           | -           |
| 23   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.995           | -           |
| 24   | adaptive      | qwen2.5-vl-7b-instruct-abliterated | 0.996           | -           |
| 25   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.991           | -           |
| 26   | hybrid        | qwen2.5-vl-7b-instruct-abliterated | 0.980           | -           |
| 27   | image         | qwen2.5-vl-7b-instruct-abliterated | 0.992           | -           |
| 28   | image         | qwen2.5-vl-7b-instruct-abliterated | 0.975           | -           |
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
