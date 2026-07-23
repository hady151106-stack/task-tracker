# Reflection — Mid-Course Project

## Tools used

GitHub Copilot Chat inside VS Code was the only AI coding assistant used, on the free tier. I used it for four distinct jobs, and the quality of the result varied sharply depending on which job it was.

The first was drafting user stories from a description of the existing system. This worked well — it produced eight well-formed stories with acceptance criteria in seconds, and it respected the constraints I set about staying inside two features and writing no code.

The second was making small, precisely specified changes to a single file, such as adding a field and a computed property to the Pydantic models. This was reliable, because there was almost nothing left to interpret.

The third was multi-point frontend integration, where I listed eight or nine numbered changes across CSS, HTML, and JavaScript in one file. This produced correct work but also produced the worst failure of the project.

The fourth was a scoped refactor of one function, where I described the problem rather than the solution. This was the cleanest single result I got.

## Where AI helped

The tag validation helper is the clearest case. I specified the rules in prose — trim, reject blanks, de-duplicate case-insensitively while keeping the first casing, cap at five — and Copilot produced a correct implementation immediately, including a detail I would probably have got wrong on a first attempt: it applies the maximum count *after* de-duplication, not before. That ordering matters. A payload of six tags where three are duplicates should be accepted as three tags, not rejected as six. Writing that by hand, I think I would have checked the length of the incoming list first because that reads more naturally.

The refactor was the other genuine win. I described the smell rather than the fix — the function both read and mutated global state through the DOM, so the source of truth was ambiguous — and it produced exactly the right restructuring, touching only that function.

## Where AI slowed me down

Twice, and in different ways.

The first was the frontend integration for due dates. Copilot implemented all eight requested changes correctly and then silently deleted three structural HTML elements: the closing `</header>` tag, the entire `<main>` element containing the board section, and the opening `div#modal-overlay`. Its summary stated that no unrelated behaviour had been changed. That claim was false. Without the board section, `getElementById("board")` returns null and the page cannot render at all.

The second was during the tags backend work. I scoped a prompt to `models.py` only. Copilot edited `models.py`, then edited `tests/test_tasks.py` to add its own tests, then attempted to run pytest through the terminal — twice, after I declined the first time. I skipped both runs. The cost here was not a bug but attention: I had to work out which of three files had changed and whether each change was one I had asked for.

Both incidents cost time, but both were caught before anything ran, because I read the diff before accepting.

## Where my review changed the result

The clearest instance is the `TaskUpdate.tags` annotation.

Copilot generated `tags: list[str] = Field(default_factory=list)` on `TaskUpdate`, the model used for PATCH. Every other field on that model is `Optional` with a `None` default, and that is not stylistic — it is what makes partial updates work, because