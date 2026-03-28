import helper_functions
import sys
from textnode import TextType, TextNode
from copy_files_to_public import copy_folder


def main():
	basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
	copy_folder("static", "docs")
	helper_functions.generate_pages_recursive("content", "template.html", "docs", basepath)

main()