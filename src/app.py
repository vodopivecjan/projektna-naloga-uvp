import os


from main.main import main


# Get the directory of the script
script_dir = os.path.abspath(os.path.dirname(__file__))

# Change working directory to that location
os.chdir(script_dir)

main()
