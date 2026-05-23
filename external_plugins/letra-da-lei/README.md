# Letra da Lei

Letra da Lei brings Brazil's legal corpus into Claude. Search statutes, codes, and regulations from official sources and get article-level results with verified
source links.

- Search Brazilian legislation by concept, keyword, or article number.
- Retrieve verbatim article text with deep links to official planalto.gov.br sources.
- List available laws by area to find the right corpus for a specific search.

## Example use cases

1. What does the Consumer Protection Code say about defective products?
2. What are the requirements to run for president under the Federal Constitution?
3. What is the statute of limitations for passive corruption under the Criminal Code?

## Tools

| Tool | What it does |
|---|---|
| `buscar_legislacao_federal` | Semantic and keyword search across the legal corpus — returns verbatim article text, citation IDs, and verified source links. Supports fast (semantic) and precise (semantic + full-text + rerank) modes. |
| `listar_legislacao_federal` | Lists all laws available in the corpus with their identifiers, thematic groupings, and source URLs. Use to discover coverage or find the right `law_key` before a targeted search. |

Both tools are read-only. Results include `retrieved_at` and `source_indexed_at` timestamps for provenance.

## When to use

- Questions about what a Brazilian law says on any topic
- Retrieving the verbatim text of a specific article, paragraph, or provision
- Verifying a citation before including it in a legal document
- Understanding rights, obligations, deadlines, or penalties under Brazilian law

## When not to use

- Legal advice — this plugin retrieves legal text; interpretation and application require a licensed Brazilian lawyer

## Skills

| Skill | Does |
|---|---|
| `/letra-da-lei:pesquisa-legislacao` | Search the Brazilian legal corpus and return cited article text |

### Links

- **Website:** https://letradalei.com
- **Documentation:** https://letradalei.com/docs
- **Support:** suporte@letradalei.com
