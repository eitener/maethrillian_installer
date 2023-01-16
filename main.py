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
			response = requests.get(RELEASE_URI)
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
			tree = ET.parse(self.localManifestPath())
			root = tree.getroot()
			published_utc = int(root.get('published_utc'))
		else:
			print("No current mod installed")
			return False
		latest_mod = self.get_latest_mod()
		if latest_mod is not None:
			for name in latest_mod.namelist():
				print(name)
				if os.path.splitext(name)[1] == '.xml':
					with latest_mod.open(name) as myfile:
						remote_manifest = myfile.read()
						print(remote_manifest)
						remote_root = ET.fromstring(remote_manifest)
						remote_published_utc = int(remote_root.get('published_utc'))
						if remote_published_utc > published_utc:
							print('I am here')
							return False
						else:
							return True
		else:
			print("No latest mod available")
			return False
		print("Unknown error. Try uninstalling and reinstalling mod.")
		return False

	def mod_cleanup(self):
		# need to delete files within the local package directory if any exist
		if os.path.isdir(self.localPkgDir()):
			for file in os.listdir(self.localPkgDir()):
				file_path = os.path.join(self.localPkgDir(), file)
				try:
					if os.path.isfile(file_path):
						os.unlink(file_path)
				except Exception as e:
					print(e)
		return "Mod removed."

	def install_mod(self):
		mod_package = self.get_latest_mod()
		if mod_package is not None:
			os.makedirs(self.localPkgDir(), exist_ok=True)
			for name in mod_package.namelist():
				if os.path.splitext(name)[1] == '.pkg':
					mod_w_path = self.localPkgPath()
				else:
					mod_w_path = self.localManifestPath()

				with mod_package.open(name) as myfile:
					with open(mod_w_path, 'wb') as f:
						f.write(myfile.read())
			print("Mod installation complete.")
		else:
			print("Unable to install mod.")

	def status(self):
		if os.path.isdir(self.localPkgDir()):
			pkg_files = [file for file in os.listdir(self.localPkgDir()) if file.endswith('.pkg')]
			manifest_files = [file for file in os.listdir(self.localPkgDir()) if file.endswith('_file_manifest.xml')]
			if len(pkg_files) == 1 and len(manifest_files) == 1 and os.path.isfile(self.localPkgPath()):
				if self.check_mod_version():
					return "Mod is installed and up to date."
				else:
					return "Mod is outdated. Press I to install latest."
			elif os.path.isfile(self.localPkgPath()):
				return "Mod is installed but files are missing or corrupted."
			else:
				return "Mod is not installed."
		else:
			return "HW2 local app data not found."


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
			print(mod_manager.mod_cleanup())
		elif cmdKey == 's' or cmdKey == 'S':
			print(mod_manager.status())
		elif cmdKey == 'q' or cmdKey == 'Q':
			quit()
		else:
			print('bad key')





