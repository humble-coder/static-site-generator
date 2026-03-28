import unittest

from textnode import TextNode, TextType, BlockType
from htmlnode import HTMLNode, LeafNode, ParentNode
from helper_functions import split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, block_to_block_type, markdown_to_html_node, extract_title

class TestTextNode(unittest.TestCase):
	def test_eq(self):
		node = TextNode("This is a text node", TextType.BOLD)
		node2 = TextNode("This is a text node", TextType.BOLD)
		self.assertEqual(node, node2)

	def test_neq(self):
		node = TextNode("This is a text node", TextType.BOLD)
		node2 = TextNode("This is a different text node", TextType.BOLD)
		self.assertNotEqual(node, node2)

	def test_repr(self):
		node = TextNode("This is a text node", TextType.ITALIC)
		self.assertEqual(repr(node), "TextNode(This is a text node, TextType.ITALIC, None)")

	def test_link(self):
		node = TextNode("This is a link", TextType.LINK, "https://www.example.com")
		self.assertEqual(node.text, "This is a link")
		self.assertEqual(node.text_type, TextType.LINK)
		self.assertEqual(node.url, "https://www.example.com")

	def test_image(self):
		node = TextNode("This is an image", TextType.IMAGE, "https://www.example.com/image.png")
		self.assertEqual(node.text, "This is an image")
		self.assertEqual(node.text_type, TextType.IMAGE)
		self.assertEqual(node.url, "https://www.example.com/image.png")

class TestSplitNodesDelimiter(unittest.TestCase):
	def test_split_nodes_delimiter_bold(self):
		nodes = [TextNode("This is *bold* text", TextType.TEXT)]
		new_nodes = split_nodes_delimiter(nodes, "*", TextType.BOLD)
		self.assertEqual(len(new_nodes), 3)
		self.assertEqual(new_nodes[0], TextNode("This is ", TextType.TEXT))
		self.assertEqual(new_nodes[1], TextNode("bold", TextType.BOLD))
		self.assertEqual(new_nodes[2], TextNode(" text", TextType.TEXT))

	def test_split_nodes_delimiter_italic(self):
		nodes = [TextNode("This is _italic_ text", TextType.TEXT)]
		new_nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
		self.assertEqual(len(new_nodes), 3)
		self.assertEqual(new_nodes[0], TextNode("This is ", TextType.TEXT))
		self.assertEqual(new_nodes[1], TextNode("italic", TextType.ITALIC))
		self.assertEqual(new_nodes[2], TextNode(" text", TextType.TEXT))

	def test_split_nodes_delimiter_code(self):
		nodes = [TextNode("This is `code` text", TextType.TEXT)]
		new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
		self.assertEqual(len(new_nodes), 3)
		self.assertEqual(new_nodes[0], TextNode("This is ", TextType.TEXT))
		self.assertEqual(new_nodes[1], TextNode("code", TextType.CODE))
		self.assertEqual(new_nodes[2], TextNode(" text", TextType.TEXT))
	
	def test_split_nodes_delimiter_no_delimiter(self):
		nodes = [TextNode("This is text without delimiter", TextType.TEXT)]
		new_nodes = split_nodes_delimiter(nodes, "*", TextType.BOLD)
		self.assertEqual(len(new_nodes), 1)
		self.assertEqual(new_nodes[0], TextNode("This is text without delimiter", TextType.TEXT))

	def test_split_nodes_delimiter_unclosed_delimiter(self):
		nodes = [TextNode("This is *bold text without closing delimiter", TextType.TEXT)]
		with self.assertRaises(Exception) as context:
			split_nodes_delimiter(nodes, "*", TextType.BOLD)
		self.assertTrue("Delimiter '*' not closed in text: 'This is *bold text without closing delimiter'" in str(context.exception))

	def test_split_nodes_delimiter_multiple_delimiters(self):
		nodes = [TextNode("This is *bold* and *another bold* text", TextType.TEXT)]
		new_nodes = split_nodes_delimiter(nodes, "*", TextType.BOLD)
		self.assertEqual(len(new_nodes), 5)
		self.assertEqual(new_nodes[0], TextNode("This is ", TextType.TEXT))
		self.assertEqual(new_nodes[1], TextNode("bold", TextType.BOLD))
		self.assertEqual(new_nodes[2], TextNode(" and ", TextType.TEXT))
		self.assertEqual(new_nodes[3], TextNode("another bold", TextType.BOLD))
		self.assertEqual(new_nodes[4], TextNode(" text", TextType.TEXT))
		
class TestExtractMarkdownImages(unittest.TestCase):
	def test_extract_markdown_images(self):
		text = "This is an image: ![alt text](https://www.example.com/image.png)"
		images = extract_markdown_images(text)
		self.assertEqual(len(images), 1)
		self.assertEqual(images[0], ("alt text", "https://www.example.com/image.png"))

	def test_extract_markdown_images_multiple(self):
		text = "This is an image: ![alt text](https://www.example.com/image.png) and another image: ![another alt text](https://www.example.com/another-image.png)"
		images = extract_markdown_images(text)
		self.assertEqual(len(images), 2)
		self.assertEqual(images[0], ("alt text", "https://www.example.com/image.png"))
		self.assertEqual(images[1], ("another alt text", "https://www.example.com/another-image.png"))

	def test_extract_markdown_images_no_images(self):
		text = "This is text without images"
		images = extract_markdown_images(text)
		self.assertEqual(len(images), 0)

class TestExtractMarkdownLinks(unittest.TestCase):
	def test_extract_markdown_links(self):
		text = "This is a link: [link text](https://www.example.com)"
		links = extract_markdown_links(text)
		self.assertEqual(len(links), 1)
		self.assertEqual(links[0], ("link text", "https://www.example.com"))

	def test_extract_markdown_links_multiple(self):
		text = "This is a link: [link text](https://www.example.com) and another link: [another link text](https://www.example.com/another-link)"
		links = extract_markdown_links(text)
		self.assertEqual(len(links), 2)
		self.assertEqual(links[0], ("link text", "https://www.example.com"))
		self.assertEqual(links[1], ("another link text", "https://www.example.com/another-link"))

	def test_extract_markdown_links_no_links(self):
		text = "This is text without links"
		links = extract_markdown_links(text)
		self.assertEqual(len(links), 0)
	
class TestSplitNodesImage(unittest.TestCase):
	def test_split_nodes_image(self):
		nodes = [TextNode("This is an image: ![alt text](https://www.example.com/image.png)", TextType.TEXT)]
		new_nodes = split_nodes_image(nodes)
		self.assertEqual(len(new_nodes), 2)
		self.assertEqual(new_nodes[0], TextNode("This is an image: ", TextType.TEXT))
		self.assertEqual(new_nodes[1], TextNode("alt text", TextType.IMAGE, "https://www.example.com/image.png"))

	def test_split_nodes_image_multiple(self):
		nodes = [TextNode("This is an image: ![alt text](https://www.example.com/image.png) and another image: ![another alt text](https://www.example.com/another-image.png)", TextType.TEXT)]
		new_nodes = split_nodes_image(nodes)
		self.assertEqual(len(new_nodes), 4)
		self.assertEqual(new_nodes[0], TextNode("This is an image: ", TextType.TEXT))
		self.assertEqual(new_nodes[1], TextNode("alt text", TextType.IMAGE, "https://www.example.com/image.png"))
		self.assertEqual(new_nodes[2], TextNode(" and another image: ", TextType.TEXT))
		self.assertEqual(new_nodes[3], TextNode("another alt text", TextType.IMAGE, "https://www.example.com/another-image.png"))

	def test_split_nodes_image_no_images(self):
		nodes = [TextNode("This is text without images", TextType.TEXT)]
		new_nodes = split_nodes_image(nodes)
		self.assertEqual(len(new_nodes), 1)
		self.assertEqual(new_nodes[0], TextNode("This is text without images", TextType.TEXT))

	def test_split_nodes_image_image_at_start(self):
		nodes = [TextNode("![alt text](https://www.example.com/image.png) This is an image", TextType.TEXT)]
		new_nodes = split_nodes_image(nodes)
		self.assertEqual(len(new_nodes), 2)
		self.assertEqual(new_nodes[0], TextNode("alt text", TextType.IMAGE, "https://www.example.com/image.png"))
		self.assertEqual(new_nodes[1], TextNode(" This is an image", TextType.TEXT))

	def test_split_nodes_image_image_at_end(self):
		nodes = [TextNode("This is an image: ![alt text](https://www.example.com/image.png)", TextType.TEXT)]
		new_nodes = split_nodes_image(nodes)
		self.assertEqual(len(new_nodes), 2)
		self.assertEqual(new_nodes[0], TextNode("This is an image: ", TextType.TEXT))
		self.assertEqual(new_nodes[1], TextNode("alt text", TextType.IMAGE, "https://www.example.com/image.png"))

class TestSplitNodesLink(unittest.TestCase):
	def test_split_nodes_link(self):
		nodes = [TextNode("This is a link: [link text](https://www.example.com)", TextType.TEXT)]
		new_nodes = split_nodes_link(nodes)
		self.assertEqual(len(new_nodes), 2)
		self.assertEqual(new_nodes[0], TextNode("This is a link: ", TextType.TEXT))
		self.assertEqual(new_nodes[1], TextNode("link text", TextType.LINK, "https://www.example.com"))

	def test_split_nodes_link_multiple(self):
		nodes = [TextNode("This is a link: [link text](https://www.example.com) and another link: [another link text](https://www.example.com/another-link)", TextType.TEXT)]
		new_nodes = split_nodes_link(nodes)
		self.assertEqual(len(new_nodes), 4)
		self.assertEqual(new_nodes[0], TextNode("This is a link: ", TextType.TEXT))
		self.assertEqual(new_nodes[1], TextNode("link text", TextType.LINK, "https://www.example.com"))
		self.assertEqual(new_nodes[2], TextNode(" and another link: ", TextType.TEXT))
		self.assertEqual(new_nodes[3], TextNode("another link text", TextType.LINK, "https://www.example.com/another-link"))

	def test_split_nodes_link_no_links(self):
		nodes = [TextNode("This is text without links", TextType.TEXT)]
		new_nodes = split_nodes_link(nodes)
		self.assertEqual(len(new_nodes), 1)
		self.assertEqual(new_nodes[0], TextNode("This is text without links", TextType.TEXT))

class TestTextToTextNodes(unittest.TestCase):
	def test_text_to_textnodes(self):
		text = "This is **bold** text with an image: ![alt text](https://www.example.com/image.png) and a link: [link text](https://www.example.com)"
		nodes = text_to_textnodes(text)
		self.assertEqual(len(nodes), 6)
		self.assertEqual(nodes[0], TextNode("This is ", TextType.TEXT))
		self.assertEqual(nodes[1], TextNode("bold", TextType.BOLD))
		self.assertEqual(nodes[2], TextNode(" text with an image: ", TextType.TEXT))
		self.assertEqual(nodes[3], TextNode("alt text", TextType.IMAGE, "https://www.example.com/image.png"))
		self.assertEqual(nodes[4], TextNode(" and a link: ", TextType.TEXT))
		self.assertEqual(nodes[5], TextNode("link text", TextType.LINK, "https://www.example.com"))

	def test_text_to_textnodes_no_markdown(self):
		text = "This is text without markdown"
		nodes = text_to_textnodes(text)
		self.assertEqual(len(nodes), 1)
		self.assertEqual(nodes[0], TextNode("This is text without markdown", TextType.TEXT))

	def test_text_to_textnodes_only_markdown(self):
		text = "**bold** ![alt text](https://www.example.com/image.png) [link text](https://www.example.com)"
		nodes = text_to_textnodes(text)
		self.assertEqual(len(nodes), 5)
		self.assertEqual(nodes[0], TextNode("bold", TextType.BOLD))
		self.assertEqual(nodes[1], TextNode(" ", TextType.TEXT))
		self.assertEqual(nodes[2], TextNode("alt text", TextType.IMAGE, "https://www.example.com/image.png"))
		self.assertEqual(nodes[3], TextNode(" ", TextType.TEXT))
		self.assertEqual(nodes[4], TextNode("link text", TextType.LINK, "https://www.example.com"))

class TestMarkdownToBlocks(unittest.TestCase):
	def test_markdown_to_blocks(self):
		text = "# Heading 1\n\nThis is a paragraph with **bold** text and an image: ![alt text](https://www.example.com/image.png) and a link: [link text](https://www.example.com)\n\n## Heading 2\n\n- List item 1\n- List item 2\n- List item 3"
		blocks = markdown_to_blocks(text)
		self.assertEqual(len(blocks), 6)
		self.assertEqual(blocks[0], "# Heading 1")
		self.assertEqual(blocks[1], "This is a paragraph with **bold** text and an image: ![alt text](https://www.example.com/image.png) and a link: [link text](https://www.example.com)")
		self.assertEqual(blocks[2], "## Heading 2")
		self.assertEqual(blocks[3], "- List item 1")
		self.assertEqual(blocks[4], "- List item 2")
		self.assertEqual(blocks[5], "- List item 3")

	def test_markdown_to_blocks_empty(self):
		text = ""
		blocks = markdown_to_blocks(text)
		self.assertEqual(len(blocks), 0)
	
	def test_markdown_to_blocks_no_newlines(self):
		text = "This is a paragraph with **bold** text and an image: ![alt text](https://www.example.com/image.png) and a link: [link text](https://www.example.com)"
		blocks = markdown_to_blocks(text)
		self.assertEqual(len(blocks), 1)
		self.assertEqual(blocks[0], "This is a paragraph with **bold** text and an image: ![alt text](https://www.example.com/image.png) and a link: [link text](https://www.example.com)")

	def test_markdown_to_blocks(self):
		md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
		blocks = markdown_to_blocks(md)
		self.assertEqual(
			blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

class TestBlockToBlockType(unittest.TestCase):
	def test_block_to_block_type_heading(self):
		block = "# Heading 1"
		block_type = block_to_block_type(block)
		self.assertEqual(block_type, BlockType.HEADING)

	def test_block_to_block_type_paragraph(self):
		block = "This is a paragraph"
		block_type = block_to_block_type(block)
		self.assertEqual(block_type, BlockType.PARAGRAPH)

	def test_block_to_block_type_code(self):
		block = "```\nThis is code\n```"
		block_type = block_to_block_type(block)
		self.assertEqual(block_type, BlockType.CODE)

	def test_block_to_block_type_quote(self):
		block = "> This is a quote"
		block_type = block_to_block_type(block)
		self.assertEqual(block_type, BlockType.QUOTE)

	def test_block_to_block_type_unordered_list(self):
		block = "- List item 1\n- List item 2\n- List item 3"
		block_type = block_to_block_type(block)
		self.assertEqual(block_type, BlockType.UNORDERED_LIST)

	def test_block_to_block_type_ordered_list(self):
		block = "1. List item 1\n2. List item 2\n3. List item 3"
		block_type = block_to_block_type(block)
		self.assertEqual(block_type, BlockType.ORDERED_LIST)

class TestExtractTitle(unittest.TestCase):
	def test_extract_title(self):
		md = """# This is the title"""
		title = extract_title(md)
		self.assertEqual(title, "This is the title")
	
	def test_extract_title_no_title(self):
		md = """This is some text without a title"""
		with self.assertRaises(ValueError) as context:
			extract_title(md)
		self.assertTrue("No title found in markdown" in str(context.exception))

if __name__ == "__main__":
	unittest.main()
