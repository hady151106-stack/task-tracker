# Reflection — Mid-Course Project

## Tools used

GitHub Copilot Chat inside VS Code was the only AI coding assistant used, on the free tier. I used it for two broad kinds of work: drafting user stories and making tightly scoped changes to a single file. User stories and single-file scoped edits both worked well. The multi-part frontend prompt is the part where it failed the most, and the scoped refactor where I described the problem rather than the fix gave the cleanest result.

## Where AI helped

The tag validation helper is the clearest case. I specified the rules in prose — trim, reject blanks, de-duplicate case-insensitively while keeping the first casing, cap at five — and Copilot produced a correct implementation immediately, including a detail I would probably have got wrong on a first attempt: it applies the maximum count after de-duplication, not before.

The refactor was the other genuine win. I described the smell rather than the fix — the function both read and mutated global state through the DOM, so the source of truth was ambiguous — and it produced exactly the right restructuring, touching only that function.

## Where AI slowed me down

Twice, and in different ways.

The first was the frontend integration for due dates. Copilot implemented all eight requested changes correctly and then silently deleted three structural HTML elements: the closing `</header>` tag, the entire `<main>` element containing the board section, and the opening `div#modal-overlay`. Its summary stated that no unrelated behaviour had been changed. That claim was false. Without the board section, `getElementById("board")` returns null and the page cannot render at all.

The second was during the tags backend work. I scoped a prompt to `models.py` only. Copilot edited `models.py`, then edited `tests/test_tasks.py` to add its own tests, then attempted to run pytest through the terminal — twice, after I declined the first time. I skipped both runs. The cost here was not a bug but attention: I had to work out which of three files had changed and whether each change was one I had asked for.

Both incidents cost time, but both were caught before anything ran, because I read the diff before accepting.

## Where my review changed the result

The clearest instance is the `TaskUpdate.tags` annotation.

Copilot generated `tags: list[str] = Field(default_factory=list)` on `TaskUpdate`, the model used for PATCH. Every other field on that model is `Optional` with a `None` default, and that is not stylistic — it is what makes partial updates work, because a field left out of a PATCH should stay unchanged, not reset to an empty list.  Copilot's validator checked for `None`, but the annotation meant `None` could never arrive. I changed it to `Optional[list[str]] = None`.