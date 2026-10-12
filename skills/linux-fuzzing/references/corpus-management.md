# Fuzzing Corpus Management: Seeds, Dictionaries, and Minimization

Technical reference for curating seed files, creating token dictionaries, and minimizing corpus bloat.

---

## 1. Assembling the Initial Seed Corpus

The quality of the initial seed corpus dictates how quickly a fuzzer achieves broad code coverage:

### Guidelines for Seed Files:
1. **Small File Size**: Seeds should ideally be $< 1\text{ KB}$ and rarely exceed $10\text{ KB}$. Large files exponentially slow down mutation processing without increasing coverage.
2. **Diverse Path Coverage**: Include files that exercise different valid features (e.g., for JSON: empty object, nested arrays, unicode strings, float numbers, boolean primitives).
3. **Valid and Near-Valid Inputs**: Fuzzers excel at mutating valid inputs across edge transitions.

---

## 2. Authoring Fuzzing Dictionaries

Dictionaries guide the mutation engine by providing protocol keywords, magic numbers, and boundary tokens:

```ini
# parser.dict - Example dictionary for HTTP/1.1 parsing
# Keyword tokens
kw_get="GET"
kw_post="POST"
kw_http="HTTP/1.1"
kw_host="Host:"
kw_content_length="Content-Length:"

# Delimiters and magic bytes
crlf="\x0d\x0a"
tab="\x09"
null_byte="\x00"

# Boundary numbers
val_max_u32="4294967295"
val_zero="0"
```
Pass to fuzzer via `-dict=parser.dict` (libFuzzer) or `-x parser.dict` (AFL++).

---

## 3. Corpus Minimization with `afl-cmin` and `libFuzzer`

Over time, a corpus accumulates redundant inputs that cover the exact same code paths.

### AFL++ Corpus Minimization (`afl-cmin`):
Removes all test files that do not trigger unique edge transitions:
```bash
afl-cmin -i raw_corpus_dir/ -o minimized_corpus_dir/ -- ./my_app @@
```

### libFuzzer Merge Mode:
Consolidates two corpus directories into a minimized set:
```bash
./fuzz_target -merge=1 minimized_corpus/ new_findings_corpus/
```
Result: `minimized_corpus` retains only the smallest files that maximize total code coverage.
