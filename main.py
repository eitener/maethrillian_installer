import os
import io
import requests
import zipfile
import xml.etree.ElementTree as ET

# not sure if I need to set this dynamically
VERSION = '1_11_2931_2'
VERSION_PTR = '1_11_2931_10'

RELEASE_URI = 'https://github.com/eitener/maethrillian/releases/latest/download/maethrillian.zip'
HW2_HOGAN_PATH = "Packages\\Microsoft.HoganThreshold_8wekyb3d8bbwe\\LocalState"

class ModManager:
	def __init__(self, appData) -> None:
		self.localStateDir = os.path.join(appData, HW2_HOGAN_PATH)
		self.version = VERSION
		if os.path.isdir(self.localPkgDir(VERSION_PTR)):
			self.version = VERSION_PTR
		
	def localPkgDir(self, version = None):	
		if version:
			return os.path.join(self.localStateDir, f"GTS\\{version}_active")
		return os.path.join(self.localStateDir, f"GTS\\{self.version}_active")
	
	def localPkgPath(self):
		return os.path.join(self.localPkgDir(), 'maethrillian.pkg')
	
	def localManifestPath(self):
		return os.path.join(self.localPkgDir(), f"{self.version}_file_manifest.xml")

	def local_mod_exists(self):
		return (os.path.isfile(self.localPkgPath()) and os.path.isfile(self.localManifestPath()))
			
	def get_latest_mod(self):
		try:
			response = requests.get(self.RELEASE_URI)
			response.raise_for_status()
		except requests.exceptions.RequestException as err:
			print("Error Occured: ",err)
			return None
		else:
			return zipfile.ZipFile(io.BytesIO(response.content))
		
	def check_mod_version(self):
		"""
		Compares local mod version to remote mod version
		"""
		if self.local_mod_exists():
			tree = ET.parse(self.localManifestPath)
			root = tree.getroot()
			published_utc = int(root.get('published_utc'))
		else:
			print("No current mod installed")
			return False
		latest_mod = self.get_latest_mod()
		if latest_mod is not None:
			for name in latest_mod.namelist():
				if os.path.splitext(name)[1] == '_file_manifest.xml':
					with latest_mod.open(name) as myfile:
						remote_manifest = myfile.read()
						remote_tree = ET.fromstring(remote_manifest)
						remote_root = remote_tree.getroot()
						remote_published_utc = int(remote_root.get('published_utc'))
						if remote_published_utc > published_utc:
							return False
							#self.install_mod()
						else:
							return True
		else:
			print("No latest mod available")
			return False

	def mod_cleanup(self):
		# need to delete files within the local package directory if any exist
		if os.path.isdir(self.localPkgDir()):
			for file in os.listdir(self.localPkgDir()):
				file_path = os.path.join(self.localPkgDir, file)
				try:
					if os.path.isfile(file_path):
						os.unlink(file_path)
				except Exception as e:
					print(e)
		#os.rmdir(self.localPkgDir)
		return

	def install_mod(self):
		try:
			response = requests.get(self.RELEASE_URI)
			response.raise_for_status()
		except requests.exceptions.RequestException as err:
			print("Error Occured: ",err)
			return False
		else:
			mod_package = zipfile.ZipFile(io.BytesIO(response.content))
			os.makedirs(self.localPkgDir, exist_ok=True)
			for name in mod_package.namelist():
				if os.path.splitext(name)[1] == '.pkg':
					mod_w_path = self.localPkgPath
				else:
					mod_w_path = self.localManifestPath

				with mod_package.open(name) as myfile:
					with open(mod_w_path, 'wb') as f:
						f.write(myfile.read())
			return True

	def status(self):
		if os.path.isfile(self.localPkgPath) and os.path.isfile(self.localManifestPath) and self.check_mod_version():
			return "Mod is installed and up to date."
		elif os.path.isdir(self.localPkgDir):
			pkg_files = [file for file in os.listdir(self.localPkgDir) if file.endswith('.pkg')]
			manifest_files = [file for file in os.listdir(self.localPkgDir) if file.endswith('_file_manifest.xml')]
			if len(pkg_files) == 1 and len(manifest_files) == 1:
				return "Mod is installed but may be out of date."
			else:
				return "Mod is installed but files are missing or corrupted."
		else:
			return "Mod is not installed."


if __name__ == '__main__':
	
	# initialize mod manager
	appData = os.environ.get('LOCALAPPDATA', -1)

	if appData == -1:
		print('Unable to find local appdata')
		input('Press any key to quit...')

	mod_manager = ModManager(appData)

	print("(I)nstall, (U)ninstall, (S)tatus, (Q)uit");

	while True:
		cmdKey = input('Enter key: ')

		if cmdKey == 'i' or cmdKey == 'I':
			mod_manager.mod_cleanup()
			mod_manager.install_mod()
		elif cmdKey == 'u' or cmdKey == 'U':
			mod_manager.mod_cleanup()
		elif cmdKey == 's' or cmdKey == 'S':
			mod_manager.status()
		elif cmdKey == 'q' or cmdKey == 'Q':
			quit()
		else:
			print('bad key')





