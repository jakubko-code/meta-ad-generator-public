#!/usr/bin/env python3
"""Compatibility notice for the retired automatic prompt translator.

The old implementation was tied to one GymBeam magnesium campaign, used a
retired SDK/model and could leave source-language literals inside prompt bodies.
Keeping that behavior would silently produce unsafe localization output.
"""

import sys


MESSAGE = """translate_prompts.py is intentionally retired.

Use BONUS/04-copy-translator/copy-translator.md with Claude Code or Codex:
  1. translate copy fields with the brand glossary;
  2. keep the brief locked and placeholders intact;
  3. run translation-mode Agents 04-08;
  4. create scoring-{lang}.json and human approval-{lang}.json;
  5. validate with generate_ads.py --lang <code> --validate-only.

No files were changed.
"""


def main() -> int:
    print(MESSAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
