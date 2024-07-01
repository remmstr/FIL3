import os
import platform
import subprocess
import shutil

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bin_dir = os.path.join(current_dir, 'bin')

    # Assurez-vous que le répertoire bin existe
    if not os.path.exists(bin_dir):
        os.makedirs(bin_dir)

    # Détecter le système d'exploitation
    system = platform.system()

    if system == "Darwin":  # macOS
        dist_path = os.path.join(bin_dir, 'mac')
        spec_file = os.path.join(current_dir, 'specs', 'main.spec')
        executable_name = 'MonApp'
        platform_tools_src = os.path.join(current_dir, 'platform-tools', 'mac')
        platform_tools_dest = os.path.join(dist_path, 'platform-tools')

    elif system == "Windows":  # Windows
        dist_path = os.path.join(bin_dir, 'windows')
        spec_file = os.path.join(current_dir, 'specs', 'main.spec')
        executable_name = 'MonApp.exe'
        platform_tools_src = os.path.join(current_dir, 'platform-tools', 'windows')
        platform_tools_dest = os.path.join(dist_path, 'platform-tools')

    else:
        raise RuntimeError("Unsupported OS")

    # Créez le répertoire dist_path s'il n'existe pas
    if not os.path.exists(dist_path):
        os.makedirs(dist_path)

    # Copier les outils de plateforme
    if os.path.exists(platform_tools_dest):
        shutil.rmtree(platform_tools_dest)
    shutil.copytree(platform_tools_src, platform_tools_dest)

    # Construire l'exécutable avec PyInstaller
    try:
        subprocess.run(['pyinstaller', spec_file, '--distpath', dist_path, '--name', executable_name], check=True)
        print(f"Executable created successfully in {dist_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error creating executable: {e}")
        exit(1)

if __name__ == "__main__":
    main()
