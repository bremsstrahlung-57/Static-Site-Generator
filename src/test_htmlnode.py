import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        
        #################
        # HTMLNode TEST #
        #################
        node = HTMLNode(
            props={"href": "https://www.google.com","target": "_blank"}
        )
        
        expected = ' href="https://www.google.com" target="_blank"'
        self.assertEqual(node.props_to_html(), expected)
        
        node_no_props = HTMLNode()
        self.assertEqual(node_no_props.props_to_html(), "")



        #################
        # LeafNode TEST #
        #################
        node1 = LeafNode("p", "This is a paragraph of text.")
        expected1 = '<p>This is a paragraph of text.</p>'
        self.assertEqual(node1.to_html(), expected1)
        
        node2 = LeafNode(
            "a",
            "Click me!",
            {"href": "https://www.google.com"}
        )
        expected2 = '<a href="https://www.google.com">Click me!</a>'
        self.assertEqual(node2.to_html(), expected2)
        
        node3 = LeafNode(None, "Just some text")
        self.assertEqual(node3.to_html(), "Just some text")
        
        with self.assertRaises(ValueError):
            LeafNode("p", "").to_html()
        with self.assertRaises(ValueError):
            LeafNode("p", None).to_html()
            
            
            
        ###################
        # ParentNode TEST #
        ###################
        p_node1 = ParentNode("p",[LeafNode("b", "Bold text"),LeafNode(None, "Normal text"),LeafNode("i", "italic text"),LeafNode(None, "Normal text"),],)
        pexp = "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"
        self.assertEqual(p_node1.to_html(),pexp)
        
        p_node2 = ParentNode("p", [
        LeafNode(None, "Just normal text here."),
        ])
        pexp2 = "<p>Just normal text here.</p>"
        self.assertEqual(p_node2.to_html(), pexp2)
        
        p_node3 = ParentNode("p", [
            LeafNode("b", "Bold text"),
            LeafNode("i", " and italic together"),
            LeafNode(None, ".")
        ])
        pexp3 = "<p><b>Bold text</b><i> and italic together</i>.</p>"
        self.assertEqual(p_node3.to_html(), pexp3)

        div_node = ParentNode("div", [
            LeafNode("h1", "Heading Text"),
            ParentNode("p", [
                LeafNode("b", "Bold in paragraph"),
                LeafNode(None, " and normal text.")
            ]),
            LeafNode("span", "Inline span text.")
        ])
        div_exp = "<div><h1>Heading Text</h1><p><b>Bold in paragraph</b> and normal text.</p><span>Inline span text.</span></div>"
        self.assertEqual(div_node.to_html(), div_exp)

        p_node5 = ParentNode("p", [
            LeafNode("b", "Bold text"),
            LeafNode(None, " and "),
            LeafNode("i", "italic text"),
            LeafNode(None, " in the same paragraph.")
        ])
        pexp5 = "<p><b>Bold text</b> and <i>italic text</i> in the same paragraph.</p>"
        self.assertEqual(p_node5.to_html(), pexp5)

if __name__ == "__main__":
    unittest.main()