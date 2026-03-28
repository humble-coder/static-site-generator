import helper_functions
from textnode import TextType, TextNode
from copy_files_to_public import copy_folder


def main():
	copy_folder("static", "public")
	helper_functions.generate_pages_recursive("content", "template.html", "public")
	#helper_functions.generate_page("content/index.md", "template.html", "public/index.html")

main()