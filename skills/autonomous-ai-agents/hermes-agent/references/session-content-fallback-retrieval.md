# Session Content Fallback Retrieval

## When FTS5 `session_search` Fails

The built-in `session_search` tool uses SQLite FTS5 full-text search on session
titles and AI responses. It can return zero results when:

- The session was created before FTS5 indexing was in place
- The query terms use character encodings FTS5 doesn't tokenize well
- The session is very old and has been pruned from the index
- The content is in user messages (which aren't indexed by default)

## Fallback: Raw JSON File Search

Session transcripts are stored as raw JSON files in `~/.hermes/sessions/`.
Use the `search_files` tool directly on this directory:

```
search_files(
    path="~/.hermes/sessions/",
    pattern="<phrase or keyword>"
)
```

This does a `grep`-style scan of all session files, finding matches in raw 
JSON content (including user messages, reasoning, tool calls, and assistant
responses that FTS5 may not have indexed).

## Extracting Full Content

Once the file is identified, read the JSON and extract the specific message:

```python
import json
path = '/home/dmin/.hermes/sessions/session_<id>.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for msg in data['messages']:
    if msg.get('role') == 'assistant' and '<keyword>' in str(msg.get('content', '')):
        print(msg['content'])
        # write to file for delivery
```

## Write to Desktop

Save extracted content as .md to the user's desktop:
```
/mnt/d/360MoveData/Users/Admin/Desktop/<文件名>.md
```

## Pitfalls

- Large session files (>1MB) may take 2-5 seconds to scan
- The pattern is case-sensitive by default — use `(?i)` prefix for case-insensitive
- Multiple sessions may contain the same phrase; present all matches to the user to disambiguate
- The JSON message array preserves full conversation history; extract only the relevant assistant response, not the entire session dump
