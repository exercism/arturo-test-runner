import pyparsing

# memoization
pyparsing.ParserElement.enable_packrat()

# common tokens
LBRACK = pyparsing.Literal("[")
RBRACK = pyparsing.Literal("]")

# nested blocks [ ... [ ... ] ... ]
nested_block = pyparsing.Forward()
nested_block << (LBRACK + pyparsing.ZeroOrMore(pyparsing.CharsNotIn("[]") | nested_block) + RBRACK)

# regular_block [ ... ]
regular_block = pyparsing.original_text_for(nested_block)
regular_block.add_parse_action(lambda t: t[0][1:-1])

# array  #[ ... ]
array_block = (pyparsing.Suppress("#") + regular_block).set_parse_action(lambda t: t[0])

# string value "..."
quoted_string = pyparsing.QuotedString('"', esc_char='\\')

# nested curly blocks { .. { ... } .. }
nested_curly = pyparsing.Forward()
nested_curly << (pyparsing.Literal("{") + pyparsing.ZeroOrMore(pyparsing.CharsNotIn("{}") | nested_curly) + pyparsing.Literal("}"))

# curly block { ... }
curly_block = pyparsing.original_text_for(nested_curly)
curly_block.add_parse_action(lambda t: t[0][1:-1])

def safe_strip_quotes(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == "'" and s[-1] == "'":
        return s[1:-1].strip()
    return s

multiline_string_or_block = (quoted_string | curly_block).set_parse_action(lambda t: safe_strip_quotes(t[0]))

# true | false
bool_value = (pyparsing.Keyword("true") | pyparsing.Keyword("false")).set_parse_action(lambda t: t[0] == "true")


def key(k):
    return pyparsing.Literal(k)


def search_first(grammar: pyparsing.ParserElement, text: str):
    results = grammar.search_string(text, max_matches=1)
    return results[0] if results else None


def search_all(grammar: pyparsing.ParserElement, text: str):
    return grammar.search_string(text)
