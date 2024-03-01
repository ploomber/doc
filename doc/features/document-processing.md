# Document processing

```{important}
The document processing API is experimental and only available for certain customers,
if you want to get on the waitlist, send us an email
[contact@ploomber.io](mailto:contact@ploomber.io)
```

Many Ploomber customers deploy LLM applications, and we're testing a set of
experimental APIs to simplify the development process.

## PDF parsing

You can parse `.pdf` files, the API will return a markdown version that you can use
to compute embeddings or pass it to an LLM.

```python
from pathlib import Path
from ploomber_cloud import document_processing


doc = Path("2024_q1_earnings_report.pdf").read_bytes()
parsed = document_processing.parse_pdf(doc=doc)
print(parsed)
```


The output is a string with the contents of the PDF in markdown format (which works
well across LLMs). The API is able to parse text, section headers and tables.

```md
# Earnings Report - Q1 2024

## Overview

In the first quarter of 2024, XYZ Corporation has demonstrated strong performance across various sectors, driving robust revenue growth and solidifying its position in the market. Despite facing some challenges in certain regions, the company's strategic initiatives and operational efficiencies have yielded positive results.

## Financial Highlights

The following table presents key financial metrics for Q1 2024:

| Metric             | Amount (in millions USD) |
|--------------------|--------------------------|
| Revenue            | $150                     |
| Net Income         | $30                      |
| Earnings per Share | $0.75                    |
| Gross Margin       | 35%                      |

## Revenue Analysis

Revenue for the quarter reached $150 million, marking a significant increase of 20% compared to the same period last year. This growth can be attributed to strong sales performance in our core markets, particularly in the technology and healthcare sectors. Additionally, our expansion into emerging markets has started to yield promising results, contributing to overall revenue growth.
```

## PowerPoint parsing

You can parse `.pptx` files, the API will return a markdown version that you can use
to compute embeddings or pass it to an LLM.

```python
from pathlib import Path
from ploomber_cloud import document_processing


doc = Path("2024_q1_earnings_presentation.pptx").read_bytes()
parsed = document_processing.parse_pptx(doc=doc)
print(parsed)
```


The output is a string with the contents of the `.pptx` in markdown format (which works
well across LLMs). The API is able to parse text, slide headers and tables.

```md
# Earnings Report - Q1 2024

---

# Overview

- **Strong Performance**: XYZ Corporation demonstrates robust revenue growth and solidifies market position.
- **Challenges Faced**: Some regional challenges, but strategic initiatives drive positive results.

---

# Financial Highlights

| Metric             | Amount (in millions USD) |
|--------------------|--------------------------|
| Revenue            | $150                     |
| Net Income         | $30                      |
| Earnings per Share | $0.75                    |
| Gross Margin       | 35%                      |

---

# Revenue Analysis

- **Revenue Growth**: Q1 2024 revenue reaches $150 million, up 20% from last year.
- **Core Markets**: Strong sales in technology and healthcare sectors.
- **Emerging Markets**: Promising results from expansion efforts.
```