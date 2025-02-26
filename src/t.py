from htmlnode import HTMLNode, LeafNode, ParentNode
from inline_markdown import *
from textnode import TextNode
markdown = """# Heading 1
        This is a **bold** paragraph with an *italic* word and a `code` snippet.
        ## Heading 2
        > This is a blockquote.
        * Item 1
        * Item 2
        
        1. Ordered Item 1
        2. Ordered Item 2"""

expected_html_node = ParentNode("div", [
            ParentNode("h1", [LeafNode(None, "Heading 1")]),
            ParentNode("p", [
                LeafNode(None, "This is a "),
                LeafNode("b", "bold"),
                LeafNode(None, " paragraph with an "),
                LeafNode("i", "italic"),
                LeafNode(None, " word and a "),
                LeafNode("code", "code"),
                LeafNode(None, " snippet."),
            ]),
            ParentNode("h2", [LeafNode(None, "Heading 2")]),
            ParentNode("blockquote", [LeafNode(None, "This is a blockquote.")]),
            ParentNode("pre", [ParentNode("code", [LeafNode(None, "This is a code block.")])]),
            ParentNode("ul", [
                ParentNode("li", [LeafNode(None, "Item 1")]),
                ParentNode("li", [LeafNode(None, "Item 2")]),
            ]),
            ParentNode("ol", [
                ParentNode("li", [LeafNode(None, "Ordered Item 1")]),
                ParentNode("li", [LeafNode(None, "Ordered Item 2")]),
            ]),
        ])

blocks = markdown_to_blocks(markdown)
parent_node = ParentNode("div", [])
i = 0
print(parent_node.children)
while i < len(blocks):
    block = blocks[i]

    print(f"\n{block}\n")

    block_type = block_to_block_type(block)
    if block_type == "paragraph":
        text_nodes = text_to_textnodes(block)
        html_nodes = [TextNode.text_node_to_html_node(node) for node in text_nodes]
        paragraph_node = ParentNode("p", html_nodes)
        parent_node.children.append(paragraph_node)

        print(f"text_nodes: {text_nodes}\nhtml_nodes: {html_nodes}\n<p>: {paragraph_node}")
        print(f"\nparent_node: {parent_node.children}\n")

        i += 1
    elif block_type == "heading":
        level = 0
        for char in block:
            if char == "#":
                level += 1
            else:
                break
        heading_text = block[level:].strip()
        text_nodes = text_to_textnodes(heading_text)
        html_nodes = [TextNode.text_node_to_html_node(node) for node in text_nodes]
        heading_node = ParentNode(f"h{level}", html_nodes)
        parent_node.children.append(heading_node)

        print(f"text_nodes: {text_nodes}\nhtml_nodes: {html_nodes}\n<h>: {heading_node}")
        print(f"\nparent_node: {parent_node.children}\n")

        i += 1
    elif block_type == "code":
        if not (block.startswith("```") and block.endswith("```")):
            raise ValueError("Code block must be enclosed with triple backticks")
        code_content = block[3:-3].strip()
        text_nodes = text_to_textnodes(code_content)
        html_nodes = [TextNode.text_node_to_html_node(node) for node in text_nodes]
        code_inner = ParentNode("code", html_nodes)
        code_outer = ParentNode("pre", [code_inner])
        parent_node.children.append(code_outer)

        print(
            f"text_nodes: {text_nodes}\nhtml_nodes: {html_nodes}\n<code>: {code_inner} </code>: {code_outer}"
        )
        print(f"\nparent_node: {parent_node.children}\n")

        i += 1
    elif block_type == "quote":
        quote_lines = []
        while i < len(blocks) and block_to_block_type(blocks[i]) == "quote":
            quote_line = blocks[i].lstrip(">").strip()
            quote_lines.append(quote_line)
            i += 1
        text_nodes = text_to_textnodes(" ".join(quote_lines))
        html_nodes = [TextNode.text_node_to_html_node(node) for node in text_nodes]
        quote_node = ParentNode("blockquote", html_nodes)
        parent_node.children.append(quote_node)

        print(f"text_nodes: {text_nodes}\nhtml_nodes: {html_nodes}\n<q>: {quote_node}")
        print(f"\nparent_node: {parent_node.children}\n")

    elif block_type == "unordered_list":
        items = []
        while (
            i < len(blocks) and block_to_block_type(blocks[i]) == "unordered_list"
        ):
            item_text = blocks[i].lstrip("*").lstrip("-").strip()
            text_nodes = text_to_textnodes(item_text)
            html_nodes = [
                TextNode.text_node_to_html_node(node) for node in text_nodes
            ]
            items.append(ParentNode("li", html_nodes))
            i += 1
        ul_node = ParentNode("ul", items)
        parent_node.children.append(ul_node)

        print(f"text_nodes: {text_nodes}\nhtml_nodes: {html_nodes}\n<ul>: {ul_node}")
        print(f"\nparent_node: {parent_node.children}\n")

    elif block_type == "ordered_list":
        items = []
        while i < len(blocks) and block_to_block_type(blocks[i]) == "ordered_list":
            item_text = re.sub(r"^\d+\.\s*", "", blocks[i]).strip()
            text_nodes = text_to_textnodes(item_text)
            html_nodes = [
                TextNode.text_node_to_html_node(node) for node in text_nodes
            ]
            items.append(ParentNode("li", html_nodes))
            i += 1
        ol_node = ParentNode("ol", items)
        parent_node.children.append(ol_node)

        print(f"text_nodes: {text_nodes}\nhtml_nodes: {html_nodes}\n<ol>: {ol_node}")
        print(f"\nparent_node: {parent_node.children}\n")

    else:
        raise ValueError(f"Unknown block type: {block_type}")
# print(parent_node)
