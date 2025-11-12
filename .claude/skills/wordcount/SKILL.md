---
name: wordcount
description: Count words in markdown, MDX, and text files. Use when the user asks about word counts, document length, or content volume for files or folders in this project.
---

# Word Count Analysis

This skill provides word count analysis for documentation and text files in the project.

## When to Use

Use this skill when the user:
- Asks "how many words are in [file/folder]?"
- Wants to know the length or size of documentation
- Requests word count statistics for markdown files
- Needs to measure documentation coverage or volume
- Asks about the scope of text content in any directory

## How It Works

The skill uses the `scripts/wordcount.py` utility located in this skill's folder which:
- Counts words in `.md`, `.mdx`, and `.txt` files
- Works on both individual files and entire directories
- Recursively processes all matching files in subdirectories
- Uses standard Python libraries (no installation required)

## Instructions

When the user requests word count information:

1. Identify the target path (file or folder) from the user's request
2. If the path is relative, resolve it relative to the project root: `/Users/metal/Development/context-for-20251112/`
3. Get the base directory path from the skill context (provided in the skill invocation message)
4. Run the wordcount script using the Bash tool:
   ```bash
   <base_directory>/scripts/wordcount.py <path>
   ```
5. Return the results to the user in a clear format

## Examples

### Count words in a single file
```bash
/Users/metal/Development/context-for-20251112/.claude/skills/wordcount/scripts/wordcount.py CLAUDE.md
```

### Count words in a directory
```bash
/Users/metal/Development/context-for-20251112/.claude/skills/wordcount/scripts/wordcount.py _context/documentation/anthropic
```

### Count words in entire documentation collection
```bash
/Users/metal/Development/context-for-20251112/.claude/skills/wordcount/scripts/wordcount.py _context/documentation
```

## Expected Output

**For a file:**
```
Word count in path/to/file.md: 1,234
```

**For a directory:**
```
Total word count in path/to/folder: 45,678
```

## Error Handling

The script will return errors if:
- Path doesn't exist
- File is not `.md`, `.mdx`, or `.txt` format
- Path is neither a file nor a directory

Handle these gracefully and suggest corrections to the user.

## Tips

- The script is executable (has shebang), so use `./scripts/wordcount.py` or the full path
- For large directories, let the user know this may take a moment
- Consider suggesting common paths like `_context/documentation/` for documentation analysis
- When showing results, provide context about what was counted (e.g., "across 47 markdown files")
