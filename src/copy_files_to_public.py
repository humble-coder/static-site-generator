import os, shutil

def copy_folder(src, dst):
	if os.path.exists(dst):
		shutil.rmtree(dst)
	print("Copying files from", src, "to", dst)
	shutil.copytree(src, dst)