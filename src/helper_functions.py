import re, os, shutil
from textnode import TextNode, TextType, BlockType
from htmlnode import HTMLNode, LeafNode, ParentNode

def split_nodes_delimiter(old_nodes, delimiter, text_type):
	new_nodes = []
	for node in old_nodes:
		if node.text_type != TextType.TEXT:
			new_nodes.append(node)
		else:
			parts = node.text.split(delimiter)
			if len(parts) % 2 == 0:
				raise Exception(f"Delimiter '{delimiter}' not closed in text: '{node.text}'")
			for i, part in enumerate(parts):
				if i % 2 == 1:
					new_nodes.extend([TextNode(part, text_type)])
				else:
					if part:
						new_nodes.extend([TextNode(part, TextType.TEXT)])
	return new_nodes

def extract_markdown_images(text):
	image_pattern = r"!\[(.*?)\]\((.*?)\)"
	matches = re.findall(image_pattern, text)
	return matches

def extract_markdown_links(text):
	link_pattern = r"\[(.*?)\]\((.*?)\)"
	matches = re.findall(link_pattern, text)
	return matches

def split_nodes_image(old_nodes):
	new_nodes = []
	for node in old_nodes:
		images = extract_markdown_images(node.text)
		if images:
			text = node.text
			for alt_text, url in images:
				sections = text.split(f"![{alt_text}]({url})", 1)
				if sections[0]:
					new_nodes.append(TextNode(sections[0], TextType.TEXT))
				new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
				text = sections[1]
			if text:
				new_nodes.append(TextNode(text, TextType.TEXT))
		else:
			if node.text:
				new_nodes.append(node)
	return new_nodes	

def split_nodes_link(old_nodes):
	new_nodes = []
	for node in old_nodes:
		links = extract_markdown_links(node.text)
		if links:
			text = node.text
			for link_text, url in links:
				sections = text.split(f"[{link_text}]({url})", 1)
				if sections[0]:
					new_nodes.append(TextNode(sections[0], TextType.TEXT))
				new_nodes.append(TextNode(link_text, TextType.LINK, url))
				text = sections[1]
			if text:
				new_nodes.append(TextNode(text, TextType.TEXT))
		else:
			if node.text:
				new_nodes.append(node)
	return new_nodes	

def text_to_textnodes(text):
	nodes = [TextNode(text, TextType.TEXT)]
	nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
	nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
	nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
	nodes = split_nodes_image(nodes)
	nodes = split_nodes_link(nodes)
	return nodes

def markdown_to_blocks(markdown):
	lines = markdown.split("\n\n")
	blocks = []
	for line in lines:
		if line.strip():
			blocks.append(line.strip())
	return blocks

def block_to_block_type(block):
	if re.match(r"^#{1,6} ", block):
		return BlockType.HEADING
	elif re.match(r"^```\n(.*?)```", block, re.DOTALL):
		return BlockType.CODE
	elif re.match(r"^> ?", block):
		return BlockType.QUOTE
	elif re.match(r"^- ", block):
		return BlockType.UNORDERED_LIST
	elif re.match(r"^\d+\. ", block):
		return BlockType.ORDERED_LIST
	else:
		return BlockType.PARAGRAPH

def text_node_to_html_node(text_node):
	if text_node.text_type == TextType.BOLD:
		return LeafNode("b", text_node.text)
	elif text_node.text_type == TextType.ITALIC:
		return LeafNode("i", text_node.text)
	elif text_node.text_type == TextType.CODE:
		return LeafNode("code", text_node.text)
	elif text_node.text_type == TextType.LINK:
		return LeafNode("a", text_node.text, {"href": text_node.url})
	elif text_node.text_type == TextType.IMAGE:
		return LeafNode("img", None, {"src": text_node.url, "alt": text_node.text})
	elif text_node.text_type == TextType.TEXT:
		return LeafNode(None, text_node.text)
	else:
		raise ValueError(f"Unknown TextType: {text_node.text_type}")

def text_to_children(text):
	text_nodes = text_to_textnodes(text)
	html_nodes = [text_node_to_html_node(node) for node in text_nodes]
	return html_nodes

def markdown_to_html_node(markdown):
	blocks = markdown_to_blocks(markdown)
	parent_node = ParentNode("div", [])
	for block in blocks:
		block_type = block_to_block_type(block)
		if block_type == BlockType.HEADING:
			level = len(re.match(r"^(#{1,6}) ", block).group(1))
			tag = f"h{level}"
			content = block[level+1:]
			html_node = ParentNode(tag, text_to_children(content))
		elif block_type == BlockType.CODE:
			content = re.match(r"^```\n(.*?)```", block, re.DOTALL).group(1)
			html_node = ParentNode("pre", [text_node_to_html_node(TextNode(content, TextType.CODE))])
		elif block_type == BlockType.QUOTE:
			content = re.sub(r"^> ?", "", block, flags=re.MULTILINE)
			html_node = ParentNode("blockquote", text_to_children(content))
		elif block_type == BlockType.UNORDERED_LIST:
			items = block.split("\n")
			items = [item[2:] for item in items]
			html_node = ParentNode("ul", [ParentNode("li", text_to_children(item)) for item in items])
		elif block_type == BlockType.ORDERED_LIST:
			items = block.split("\n")
			items = [re.sub(r"^\d+\. ","", item) for item in items]
			html_node = ParentNode("ol", [ParentNode("li", text_to_children(item)) for item in items])
		else:
			content = block.replace("\n", " ")
			html_node = ParentNode("p", text_to_children(content))
		parent_node.children.append(html_node)
	return parent_node

def extract_title(markdown):
	lines = markdown.split("\n")
	for line in lines:
		if line.startswith("# "):
			if line[2:].strip():
				return line[2:].strip()
	raise ValueError("No title found in markdown")

def generate_page(from_path, template_path, dest_path, basepath):
	print("Generating page from", from_path, "using template", template_path, "and saving to", dest_path)
	with open(from_path, "r") as f:
		markdown = f.read()
	html_node = markdown_to_html_node(markdown)
	html_content = html_node.to_html()
	title = extract_title(markdown)
	with open(template_path, "r") as f:
		template = f.read()
	page_content = template.replace("{{ Title }}", title).replace("{{ Content }}", html_content).replace('href="/', f'href="{basepath}').replace('src="/', f'src="{basepath}')
	if not os.path.exists(os.path.dirname(dest_path)):
		os.makedirs(os.path.dirname(dest_path))
	with open(dest_path, "w") as f:
		f.write(page_content)

def generate_pages_recursive(content_dir, template_path, dest_dir, basepath):
	for root, dirs, files in os.walk(content_dir):
		for file in files:
			if file.endswith(".md"):
				rel_path = os.path.relpath(os.path.join(root, file), content_dir)
				dest_path = os.path.join(dest_dir, rel_path[:-3] + ".html")
				generate_page(os.path.join(root, file), template_path, dest_path, basepath)