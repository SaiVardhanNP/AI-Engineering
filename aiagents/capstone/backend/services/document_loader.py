import re
from pathlib import Path

FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
HEADING = re.compile(r"^(#{1,3})\s+(.*)$", re.MULTILINE)

# MDX leftovers that carry no meaning for retrieval: {/* comments */} and
# lines holding only a component tag such as <Tabs>, </TabPanel>, </Admonition>
MDX_NOISE = re.compile(
    r"^[ \t]*(\{/\*.*?\*/\}|</?[A-Z][A-Za-z]*[^>\n]*>)[ \t]*$\n?",
    re.MULTILINE,
)


class DocumentLoader:
    """Loads markdown/mdx docs and splits them into section-aware chunks."""

    def __init__(self, base_url="", max_chars=1500, min_chars=200):
        self.base_url = base_url.rstrip("/")
        self.max_chars = max_chars
        self.min_chars = min_chars

    def load_directory(self, root):
        root = Path(root)
        chunks = []

        for path in sorted([*root.rglob("*.md"), *root.rglob("*.mdx")]):
            chunks.extend(self.load_file(path, root))

        return chunks

    def load_file(self, path, root):
        raw = path.read_text(encoding="utf-8")
        title, body = self._split_frontmatter(raw, path)
        body = MDX_NOISE.sub("", body)
        url = self._build_url(path, root)

        chunks = []

        for section, text in self._split_sections(body):
            for piece in self._split_long(text):
                chunks.append(
                    {
                        "text": piece,
                        "title": title,
                        "section": section,
                        "url": url,
                    }
                )

        return chunks

    def _split_frontmatter(self, raw, path):
        title = path.stem.replace("-", " ").replace("_", " ").title()

        match = FRONTMATTER.match(raw)
        if not match:
            return title, raw

        for line in match.group(1).splitlines():
            key, _, value = line.partition(":")
            if key.strip() == "title" and value.strip():
                title = value.strip().strip("\"'")

        return title, raw[match.end():]

    def _split_sections(self, body):
        sections = []
        current_heading = "Overview"
        last_end = 0

        for match in HEADING.finditer(body):
            text = body[last_end:match.start()].strip()
            if text:
                sections.append((current_heading, text))
            current_heading = match.group(2).strip()
            last_end = match.end()

        tail = body[last_end:].strip()
        if tail:
            sections.append((current_heading, tail))

        return self._merge_short_sections(sections)

    def _merge_short_sections(self, sections):
        # a short section is usually a lead-in ("The following variables are
        # available:") so attach it, with its heading, to the section after it
        merged = []
        carry = ""

        for heading, text in sections:
            if carry:
                text = f"{carry}\n\n{text}"
                carry = ""

            if len(text) < self.min_chars:
                carry = f"{heading}\n{text}"
            else:
                merged.append((heading, text))

        if carry:
            if merged:
                heading, text = merged[-1]
                merged[-1] = (heading, f"{text}\n\n{carry}")
            else:
                merged.append(("Overview", carry))

        return merged

    def _split_long(self, text):
        if len(text) <= self.max_chars:
            return [text]

        pieces = []

        for piece in self._pack(text.split("\n\n"), "\n\n"):
            if len(piece) > self.max_chars:
                # tables and code blocks have no blank lines, so cut by line
                pieces.extend(self._pack(piece.split("\n"), "\n"))
            else:
                pieces.append(piece)

        return pieces

    def _pack(self, units, separator):
        packed = []
        current = ""

        for unit in units:
            if current and len(current) + len(unit) > self.max_chars:
                packed.append(current.strip())
                current = ""
            current += unit + separator

        if current.strip():
            packed.append(current.strip())

        return packed

    def _build_url(self, path, root):
        relative = path.relative_to(root).with_suffix("").as_posix()
        return f"{self.base_url}/{relative}" if self.base_url else relative
