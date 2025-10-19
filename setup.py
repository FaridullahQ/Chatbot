#!/usr/bin/env python3
"""
QaderiChat Setup Script
Automates the initial setup process for the Django chatbot application.
"""

import os
import sys
import subprocess
import secrets
import shutil
from pathlib import Path


def run_command(command, description=""):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        return None


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required.")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        
        # Generate a random secret key
        secret_key = secrets.token_urlsafe(50)
        
        # Read and update the .env file
        with open(env_file, 'r') as f:
            content = f.read()
        
        content = content.replace('your_secret_key_here', secret_key)
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Created .env file with generated secret key")
        print("⚠️  Please add your OpenAI API key to the .env file")
    else:
        print("ℹ️  .env file already exists")


def setup_virtual_environment():
    """Create and activate virtual environment."""
    venv_path = Path('venv')
    
    if not venv_path.exists():
        run_command(f"{sys.executable} -m venv venv", "Creating virtual environment")
    else:
        print("ℹ️  Virtual environment already exists")
    
    # Determine the correct activation script path
    if os.name == 'nt':  # Windows
        activate_script = venv_path / 'Scripts' / 'activate'
        pip_path = venv_path / 'Scripts' / 'pip'
    else:  # Unix/Linux/macOS
        activate_script = venv_path / 'bin' / 'activate'
        pip_path = venv_path / 'bin' / 'pip'
    
    return str(pip_path)


def install_dependencies(pip_path):
    """Install Python dependencies."""
    run_command(f"{pip_path} install --upgrade pip", "Upgrading pip")
    run_command(f"{pip_path} install -r requirements.txt", "Installing dependencies")


def setup_database():
    """Set up the database."""
    run_command("python manage.py makemigrations", "Creating database migrations")
    run_command("python manage.py migrate", "Applying database migrations")


def create_superuser():
    """Prompt to create a superuser."""
    response = input("\n🤔 Would you like to create a superuser account? (y/n): ").lower()
    if response in ['y', 'yes']:
        run_command("python manage.py createsuperuser", "Creating superuser")


def collect_static_files():
    """Collect static files."""
    run_command("python manage.py collectstatic --noinput", "Collecting static files")


def run_tests():
    """Run the test suite."""
    response = input("\n🤔 Would you like to run the test suite? (y/n): ").lower()
    if response in ['y', 'yes']:
        run_command("python manage.py test", "Running tests")


def main():
    """Main setup function."""
    print("🚀 QaderiChat Setup Script")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Create .env file
    create_env_file()
    
    # Setup virtual environment
    print("\n📦 Setting up virtual environment...")
    pip_path = setup_virtual_environment()
    
    # Install dependencies
    print("\n📚 Installing dependencies...")
    install_dependencies(pip_path)
    
    # Setup database
    print("\n🗄️  Setting up database...")
    setup_database()
    
    # Collect static files
    print("\n📁 Collecting static files...")
    collect_static_files()
    
    # Create superuser
    create_superuser()
    
    # Run tests
    run_tests()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Add your OpenAI API key to the .env file")
    print("2. Activate the virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("3. Start the development server:")
    print("   python manage.py runserver")
    print("4. Open http://127.0.0.1:8000 in your browser")
    print("\n🤖 Enjoy chatting with QaderiChat!")


if __name__ == "__main__":
    main()
