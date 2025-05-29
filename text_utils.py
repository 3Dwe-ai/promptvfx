import re


def snake_case(text: str) -> str:
    return re.sub(r"[\s]+", "_", text.strip()).lower()


def as_markdown_code(code: str) -> str:
    return f"```\n{code}\n```"


def extract_code(markdown: str) -> str:
    pattern = re.compile(r"```(?:\w+)?\n(.*?)\n```", re.DOTALL)
    match = pattern.search(markdown)
    return match.group(1) if match else ""


def build_function_inspector_markdown(
    centers_code: str, rgbs_code: str, opacities_code: str
) -> str:
    return FUNCTION_INSPECTOR_MARKDOWN_TEMPLATE.format(
        centers_code=centers_code, rgbs_code=rgbs_code, opacities_code=opacities_code
    )


FUNCTION_INSPECTOR_MARKDOWN_TEMPLATE = """
##### Centers
```python
{centers_code}
```
<br/><br/>
##### RGBs
```python
{rgbs_code}
```
<br/><br/>
##### Opacities
```python
{opacities_code}
```
""".strip()
