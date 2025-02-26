import unittest
from inline_markdown import (
    text_to_textnodes,
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
    markdown_to_blocks,
    block_to_block_type,
    markdown_to_html_node
)

from textnode import TextNode, TextType
from htmlnode import ParentNode, LeafNode


class TestInlineMarkdown(unittest.TestCase):
    ##############################
    # test_split_nodes_delimiter #
    ##############################
    def test_delim_bold(self):
        node = TextNode("This is text with a **bolded** word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded", TextType.BOLD),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_delim_bold_double(self):
        node = TextNode(
            "This is text with a **bolded** word and **another**", TextType.TEXT
        )
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded", TextType.BOLD),
                TextNode(" word and ", TextType.TEXT),
                TextNode("another", TextType.BOLD),
            ],
            new_nodes,
        )

    def test_delim_bold_multiword(self):
        node = TextNode(
            "This is text with a **bolded word** and **another**", TextType.TEXT
        )
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded word", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("another", TextType.BOLD),
            ],
            new_nodes,
        )

    def test_delim_italic(self):
        node = TextNode("This is text with an *italic* word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_delim_bold_and_italic(self):
        node = TextNode("**bold** and *italic*", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        new_nodes = split_nodes_delimiter(new_nodes, "*", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
            ],
            new_nodes,
        )

    def test_delim_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    ###########################
    # extract_markdown_images #
    ###########################
    # extract_markdown_links  #
    ###########################
    def test_extract_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        expected = extract_markdown_images(text)
        self.assertListEqual(
            expected,
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
        )

    def test_extract_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        expected = extract_markdown_links(text)
        self.assertListEqual(
            expected,
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
        )

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a [link](https://boot.dev) and [another link](https://blog.boot.dev)"
        )
        self.assertListEqual(
            [
                ("link", "https://boot.dev"),
                ("another link", "https://blog.boot.dev"),
            ],
            matches,
        )

    def test_no_markdown(self):
        text = "This is plain text with no markdown"
        self.assertEqual(extract_markdown_images(text), [])
        self.assertEqual(extract_markdown_links(text), [])

    #####################
    # split_nodes_image #
    #####################
    # split_nodes_link  #
    #####################
    def test_split_link(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        self.assertListEqual(
            split_nodes_link([node]),
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
        )

    def test_split_image(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            ],
            new_nodes,
        )

    def test_split_image_single(self):
        node = TextNode(
            "![image](https://www.example.COM/IMAGE.PNG)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://www.example.COM/IMAGE.PNG"),
            ],
            new_nodes,
        )

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](https://boot.dev) and [another link](https://blog.boot.dev) with text that follows",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("another link", TextType.LINK, "https://blog.boot.dev"),
                TextNode(" with text that follows", TextType.TEXT),
            ],
            new_nodes,
        )

    #####################
    # text_to_textnodes #
    #####################
    def test_text_to_textnodes(self):
        nodes = text_to_textnodes(
            "This is **text** with an *italic* word and a `code block` and an ![image](https://i.imgur.com/zjjcJKZ.png) and a [link](https://boot.dev)"
        )
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )
    def test_text_to_textnodes_bold(self):
        nodes = text_to_textnodes(
            "This is **text** with an bold word"
        )
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an bold word", TextType.TEXT)
            ],
            nodes,
        )
    def test_text_to_textnodes_link(self):
        nodes = text_to_textnodes(
            "[link](https://boot.dev)"
        )
        self.assertListEqual(
            [
                TextNode("link", TextType.LINK, "https://boot.dev")
            ],
            nodes,
        )
    def test_text_to_textnodes_image(self):
        nodes = text_to_textnodes(
            "This is an image ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual(
            [
                TextNode("This is an image ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png")
            ],
            nodes,
        )
    def test_text_to_textnodes_text(self):
        nodes = text_to_textnodes(
            "This is text"
        )
        self.assertListEqual(
            [
                TextNode("This is text", TextType.TEXT)
            ],
            nodes,
        )
    def test_text_to_textnodes_empty(self):
        nodes = text_to_textnodes(
            ""
        )
        self.assertListEqual(
            [],
            nodes,
        )

    ######################
    # markdown_to_blocks #
    ######################
    def test_markdown_to_blocks(self):
        markdown = """# This is a heading
        This is a paragraph of text. It has some **bold** and *italic* words inside of it.
        * This is the first list item in a list block
        * This is a list item
        * This is another list item"""
        self.assertListEqual(markdown_to_blocks(markdown), ["# This is a heading","This is a paragraph of text. It has some **bold** and *italic* words inside of it.","* This is the first list item in a list block","* This is a list item","* This is another list item"])

    def test_markdown_one_line(self):
        md = " # This is a sentence"
        expected_result = ["# This is a sentence"]
        self.assertListEqual(markdown_to_blocks(md), expected_result)

    def test_markdown_blank(self):
        md1 = " "
        md2 = ""
        self.assertListEqual(markdown_to_blocks(md1),[''])
        self.assertListEqual(markdown_to_blocks(md2),[''])

    #######################
    # block_to_block_type #
    #######################
    def test_block_heading(self):
        heading = "# This is a heading"
        expected = "heading"
        self.assertEqual(block_to_block_type(heading),expected)

    def test_block_code(self):
        code = "```print(\"hello world\")```"
        expected = "code"
        self.assertEqual(block_to_block_type(code), expected)

    def test_block_quote(self):
        quote = "> We are not given a short life, but we make it short, and we are not ill-supplied but wasteful of it."
        expected = "quote"
        self.assertEqual(block_to_block_type(quote),expected)

    def text_block_unordered_list(self):
        unordered_list = "* This is another list item"
        expected = "unordered_list"
        self.assertEqual(block_to_block_type(unordered_list),expected)

    def text_block_ordered_list(self):
        ordered_list = "1. This is another list item"
        expected = "ordered_list"
        self.assertEqual(block_to_block_type(ordered_list),expected)

    def test_block_paragraph(self):
        para = "This is a paragraph of text. It has some **bold** and *italic* words inside of it."
        expected = "paragraph"
        self.assertEqual(block_to_block_type(para), expected)
        
    
    def test_markdown_to_html_node(self):
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

        result = markdown_to_html_node(markdown)
        print(result)
        # self.assertEqual(result.to_html(), expected_html_node.to_html())
    

if __name__ == "__main__":
    unittest.main()
