class HTMLNode():
	
	def __init__(self, tag=None, value=None, children=None, props=None):
		self.tag = tag
		self.value = value
		self.children = children
		self.props = props

	def __eq__(self, value):
		return self.tag == value.tag and self.value == value.value and self.children == value.children and self.props == value.props

	def to_html(self):
		raise NotImplementedError("to_html method must be implemented by subclasses")
	
	def props_to_html(self):
		if self.props is None:
			return ""
		return " " + " ".join(f'{key}="{value}"' for key, value in self.props.items())
	
	def __repr__(self):
		return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"

class LeafNode(HTMLNode):
	
	def __init__(self, tag=None, value=None, props=None):
		super().__init__(tag, value, None, props)

	def to_html(self):
		if self.tag is None:
			return self.value
		if self.value is None:
			if self.tag in ["img", "br", "hr"]:
				return f"<{self.tag}{self.props_to_html()} />"
			else:
				raise ValueError(f"{self.tag} LeafNode must have a value")
		return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"	
	
	def __repr__(self):
		return f"LeafNode({self.tag}, {self.value}, {self.props})"

class ParentNode(HTMLNode):
	
	def __init__(self, tag, children, props=None):
		super().__init__(tag, None, children, props)

	def to_html(self):
		if self.tag is None:
			raise ValueError("ParentNode must have a tag")
		if self.children is None:
			raise ValueError("ParentNode must have children")
		children_html = "".join(child.to_html() for child in self.children)
		return f"<{self.tag}{self.props_to_html()}>{children_html}</{self.tag}>"
	
	def __repr__(self):
		return f"ParentNode({self.tag}, {self.children}, {self.props})"