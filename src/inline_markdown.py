import re

from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        split_nodes = []
        sections = old_node.text.split(delimiter)
        if len(sections) % 2 == 0:
            raise ValueError("Invalid markdown, formatted section not closed")
        for i in range(len(sections)):
            if sections[i] == "":
                continue
            if i % 2 == 0:
                split_nodes.append(TextNode(sections[i], TextType.TEXT))
            else:
                split_nodes.append(TextNode(sections[i], text_type))
        new_nodes.extend(split_nodes)
    return new_nodes


def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        original_text = old_node.text
        images = extract_markdown_images(original_text)
        if len(images) == 0:
            new_nodes.append(old_node)
            continue
        for image in images:
            sections = original_text.split(f"![{image[0]}]({image[1]})", 1)
            if len(sections) != 2:
                raise ValueError("Invalid markdown, image section not closed")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(
                TextNode(
                    image[0],
                    TextType.IMAGE,
                    image[1],
                )
            )
            original_text = sections[1]
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        original_text = old_node.text
        links = extract_markdown_links(original_text)
        if len(links) == 0:
            new_nodes.append(old_node)
            continue
        for link in links:
            sections = original_text.split(f"[{link[0]}]({link[1]})", 1)
            if len(sections) != 2:
                raise ValueError("Invalid markdown, link section not closed")
            if sections[0] != "":
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            new_nodes.append(TextNode(link[0], TextType.LINK, link[1]))
            original_text = sections[1]
        if original_text != "":
            new_nodes.append(TextNode(original_text, TextType.TEXT))
    return new_nodes


def extract_markdown_images(text):
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def extract_markdown_links(text):
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def markdown_to_blocks(markdown):
    markdown_c = markdown
    md_list = markdown_c.split("\n")
    newMdList = [x.strip() for x in md_list]
    return newMdList

def block_to_block_type(markdown_block):
    blocks = {
        0: "paragraph",
        1: "heading",
        2: "code",
        3: "quote",
        4: "unordered_list",
        5: "ordered_list"
    }
    parts = markdown_block.split(" ")
    if bool(re.match(r"^#{1,6}", parts[0])):
        return blocks[1]
    elif bool(re.match(r"^`{3}", parts[0])):
        if len(parts) == 1:
            if bool(re.match(r"`{3}", parts[0])):
                return blocks[2]
        else:
            if bool(re.match(r"`{3}", parts[-1][-3:])):
                return blocks[2]
    elif bool(re.match("^>",parts[0])):
        return blocks[3]
    elif bool(re.match("^\*",parts[0])):
        return blocks[4]
    elif bool(re.match("^\d+\.$", parts[0])):
        return blocks[5]
    else:
        return blocks[0]


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    parent_node = ParentNode("div", [])
    i = 0
    while i < len(blocks):
        block = blocks[i]
        block_type = block_to_block_type(block)
        if block_type == "paragraph":
            text_nodes = text_to_textnodes(block)
            html_nodes = [TextNode.text_node_to_html_node(node) for node in text_nodes]
            paragraph_node = ParentNode("p", html_nodes)
            parent_node.children.append(paragraph_node)
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
        else:
            raise ValueError(f"Unknown block type: {block_type}")
    return parent_node
