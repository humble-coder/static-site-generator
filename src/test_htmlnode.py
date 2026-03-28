from platform import node
import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextNode, TextType
from helper_functions import text_node_to_html_node, markdown_to_html_node

class TestHtmlNode(unittest.TestCase):
	def test_eq(self):
		node = HTMLNode("div", None, None, {"class": "container"})
		node2 = HTMLNode("div", None, None, {"class": "container"})
		self.assertEqual(node, node2)
		node3 = HTMLNode("p", "Some text", None, None)
		node4 = HTMLNode("p", "Some text", None, None)
		self.assertEqual(node3, node4)
 
	def test_neq(self):
		node = HTMLNode("div", None, None, {"class": "container"})
		node2 = HTMLNode("span", None, None, {"class": "container"})
		self.assertNotEqual(node, node2)

	def test_repr(self):
		node = HTMLNode("div", None, None, {"class": "container"})
		self.assertEqual(repr(node), "HTMLNode(div, None, None, {'class': 'container'})")

	def test_props_to_html(self):
		node = HTMLNode("div", None, None, {"class": "container"})
		self.assertEqual(node.props_to_html(), ' class="container"')	

class TestLeafNode(unittest.TestCase):
	def test_to_html(self):
		node = LeafNode("p", "Some text", {"class": "text"})
		self.assertEqual(node.to_html(), '<p class="text">Some text</p>')
	
	def test_leaf_to_html_p(self):
		node = LeafNode("p", "Hello, world!")
		self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

	def test_leaf_to_html_span(self):
		node = LeafNode("span", "Hello, world!", {"style": "color: red;"})
		self.assertEqual(node.to_html(), '<span style="color: red;">Hello, world!</span>')
	
	def test_leaf_to_html_no_tag(self):
		node = LeafNode(None, "Just text")
		self.assertEqual(node.to_html(), "Just text")

class TestParentNode(unittest.TestCase):
	def test_to_html(self):
		child1 = LeafNode("p", "Paragraph 1")
		child2 = LeafNode("p", "Paragraph 2")
		parent = ParentNode("div", [child1, child2], {"class": "container"})
		self.assertEqual(parent.to_html(), '<div class="container"><p>Paragraph 1</p><p>Paragraph 2</p></div>')

	def test_to_html_with_children(self):
		child_node = LeafNode("span", "child")
		parent_node = ParentNode("div", [child_node])
		self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

	def test_to_html_with_grandchildren(self):
		grandchild_node = LeafNode("b", "grandchild")
		child_node = ParentNode("span", [grandchild_node])
		parent_node = ParentNode("div", [child_node])
		self.assertEqual(
			parent_node.to_html(),
			"<div><span><b>grandchild</b></span></div>",
		)

class TestTextNodeToHtmlNode(unittest.TestCase):
	def test_text_node_to_html_node_bold(self):
		text_node = TextNode("Bold text", TextType.BOLD)
		html_node = text_node_to_html_node(text_node)
		self.assertEqual(html_node.to_html(), "<b>Bold text</b>")

	def test_text_node_to_html_node_italic(self):
		text_node = TextNode("Italic text", TextType.ITALIC)
		html_node = text_node_to_html_node(text_node)
		self.assertEqual(html_node.to_html(), "<i>Italic text</i>")

class TestMarkdownToHtmlNode(unittest.TestCase):
	def test_markdown_to_html_node_heading(self):
		markdown = "# Heading"
		html_node = markdown_to_html_node(markdown)
		self.assertEqual(html_node.to_html(), "<div><h1>Heading</h1></div>")

	def test_markdown_to_html_node_paragraph(self):
		markdown = "This is a paragraph."
		html_node = markdown_to_html_node(markdown)
		self.assertEqual(html_node.to_html(), "<div><p>This is a paragraph.</p></div>")

	def test_paragraphs(self):
		md = """
This is **bolded** paragraph
text in a p
tag here	

This is another paragraph with _italic_ text and `code` here

"""
		node = markdown_to_html_node(md)
		html = node.to_html()
		self.assertEqual(
			html,
        	"<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
    	)

	def test_codeblock(self):
		md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""
		node = markdown_to_html_node(md)
		html = node.to_html()
		self.assertEqual(
			html,
			"<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
		)


if __name__ == "__main__":
	unittest.main()