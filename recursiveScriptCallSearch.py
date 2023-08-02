import os
import json
import re
import subprocess
import sys

# POPULATE VARIABLES 
# ==============================================
log_file = "missing_files.txt"
completeJson = "file_structure.json"
#groovy_file_path = r"C:\Users\aseferagic\OneDrive - ENDAVA\Work\NXP Ranger5 July 2023\ROM-repo\aa-sca---uwb-sw---rom\onic\ROM\toolsupport\jenkinsfile"
groovy_file_path = r"C:\Users\aseferagic\OneDrive - ENDAVA\Work\NXP Ranger5 July 2023\aa-sca---uwb-sw---sbe\onall\toolsupport\jenkins\jenkinsfile"
used_file = "used_scripts.txt"
# ==============================================

pathDelimiter = "\\" if os.name == 'nt' else "/"

with open(used_file, "w") as f:
    f.write("===========================================================\n")
    f.write(f"All scripts used in '{groovy_file_path}' or its children:" + "\n")
    f.write("===========================================================\n") 

def extractRepoNameFromPath(path):
    pattern = r"aa.*?---.*?---.*?[\\\/]"
    match = re.search(pattern, path)
    if match:
        extracted_value = match.group()
        # Need to cut off the last character "\" or "/" matched by regex
        reponame = extracted_value[:-1] + pathDelimiter
        return reponame
    else:
        print(f"path={path} does not contain Git repository with a name adhering to NXP convention (aa-sca---X---Y)")
        sys.exit(1)

reponame = extractRepoNameFromPath(groovy_file_path)
# Extract Git repository name from groovy_file_path (e.g. "C:\Users\aseferagic\OneDrive - ENDAVA\Work\NXP Ranger5 July 2023\ROM-repo\aa-sca---uwb-sw---rom")
substring_start = groovy_file_path.index(reponame)
substring_end = groovy_file_path.index(pathDelimiter, substring_start)
root_repository_local_path = groovy_file_path[:substring_end]

def initLogFile(log_file, jenkinsfile):
    with open(log_file, "w") as f:
            f.write("===========================================================\n")
            f.write(f"Missing files in tree with root '{jenkinsfile}':" + "\n")
            f.write("===========================================================\n")

def appendFilepath(path):
    # Check if already exists
    append = False
    with open(used_file, 'r') as file:
        content = file.read()
        if path not in content:
            append = True
    
    # Log shortened file path to a txt file if it already isn't added
    if append:
        with open(used_file, "a") as f:
            f.write(path + "\n")

def find_file_paths_from_path(file_path, root_path, json, parent_json_array, log_file, pathDelimiter, reponame):
    # Check if the file_path exists before trying to open it
    if not os.path.exists(file_path):
        with open(log_file, "a") as f:
            f.write(file_path + "\n")
        return

    with open(file_path, 'r') as file:
        content = file.read()

        # Search for file paths with extensions '.bat', '.py' and '.mmf'
        paths = re.findall(r'[\'"]([^\'"\s]*\.(bat|py))', content)

        paths = [path[0].replace('/', pathDelimiter) for path in paths]

        # Process each found file path
        for path in paths:
            # Remove '%~dp0' from the beginning of the string if present
            if path.startswith("%~dp0"):
                path = path.replace("%~dp0", "", 1)

            if path.find(root_path) == -1:
                if path.count('..') > 0 and path.startswith('..'):
                    # Count occurrences of '..' in the path
                    N = path.count('..')

                    # Remove part of the string from last Nth backslash until the end
                    path_parts = root_path.split(pathDelimiter)
                    new_root_path = pathDelimiter.join(path_parts[:-N]) if N > 0 else root_path

                    path_parts = path.split(pathDelimiter)
                    new_path = pathDelimiter.join(path_parts[N:]) if N > 0 else path

                    # Concatenate the new path with the root path
                    path = os.path.join(new_root_path, new_path)
                #elif path.count('..') > 0 and not path.startswith('..'):
                #    # TODO how to handle paths like '%PROJECT_HOME%\..\onall\toolsupport\doxygen\run_doxygen.bat' that include environment variables
                #    path
                else:
                    path = root_path + pathDelimiter + path

            json_rootfile = file_path.split(reponame, 1)[-1]
            json_path = path.split(reponame, 1)[-1]

            json_to_compare = None
            # Check if parent_json_array is empty
            if not parent_json_array:
                json_to_compare = json
            else:
                # Traverse the parent_json_array and access the nested JSON values
                current_json = json
                for key in parent_json_array:
                    current_json = current_json.get(key)
                    if current_json is None:
                        break
                json_to_compare = current_json

            if json_rootfile in json_to_compare and json_to_compare[json_rootfile] == []:
                # Traverse the parent_json_array and access the nested JSON values
                if not parent_json_array:
                    if json[json_rootfile] == []:
                        json[json_rootfile] = {json_path : []}
                        appendFilepath(json_path)
                else:
                    current_json = json
                    for key in parent_json_array:
                        current_json = current_json[key]
                        if json_rootfile in current_json and current_json[json_rootfile] == []:
                            current_json[json_rootfile] = {json_path : []}
                            appendFilepath(json_path)                          
                        elif json_rootfile in current_json and not current_json[json_rootfile] == []:
                            current_json[json_rootfile] += "," + {json_path : []}
                            appendFilepath(json_path)                         
                        if current_json is None:
                            break
            else:
                # Not only item, append to existing
                temp_obj = json_to_compare[json_rootfile]
                temp_obj[json_path] = []
                appendFilepath(json_path)             

            #print("--------------------JSON------------------")
            #print(json)
            #print("---------------------------------------")

            last_backslash_index = path.rfind(pathDelimiter)
            new_root = path[:last_backslash_index]

            # Recursively search for file paths in referenced files
            sub_parent_json_array = parent_json_array.copy()
            sub_parent_json_array.append(json_rootfile)
            find_file_paths_from_path(path, new_root, json, sub_parent_json_array, log_file, pathDelimiter, reponame)

def find_file_paths_in_string(content, file_path, root_path, json, parent_json_array, log_file, pathDelimiter, reponame):
    # Search for file paths with extensions '.bat', '.py' and '.mmf'
    paths = re.findall(r'[\'"]([^\'"\s]*\.(bat|py))', content)

    paths = [path[0].replace('/', pathDelimiter) for path in paths]

    # Process each found file path
    for path in paths:
        # Remove '%~dp0' from the beginning of the string if present
        if path.startswith("%~dp0"):
            path = path.replace("%~dp0", "", 1)

        if path.find(root_path) == -1:
            if path.count('..') > 0 :
                # Count occurrences of '..' in the path
                N = path.count('..')

                # Remove part of the string from last Nth backslash until the end
                path_parts = root_path.split(pathDelimiter)
                new_root_path = pathDelimiter.join(path_parts[:-N]) if N > 0 else root_path

                path_parts = path.split(pathDelimiter)
                new_path = pathDelimiter.join(path_parts[N:]) if N > 0 else path

                # Concatenate the new path with the root path
                path = os.path.join(new_root_path, new_path)
            else:
                path = root_path + pathDelimiter + path

        json_rootfile = file_path.split(reponame, 1)[-1]
        json_path = path.split(reponame, 1)[-1]

        json_to_compare = None
        # Check if parent_json_array is empty
        if not parent_json_array:
            json_to_compare = json
        else:
            # Traverse the parent_json_array and access the nested JSON values
            current_json = json
            for key in parent_json_array:
                current_json = current_json.get(key)
                if current_json is None:
                    break
            json_to_compare = current_json

        if json_rootfile in json_to_compare and json_to_compare[json_rootfile] == []:
            # Traverse the parent_json_array and access the nested JSON values
            if not parent_json_array:
                if json[json_rootfile] == []:
                    json[json_rootfile] = {json_path : []}
                    appendFilepath(json_path)
            else:
                current_json = json
                for key in parent_json_array:
                    current_json = current_json[key]
                    if json_rootfile in current_json and current_json[json_rootfile] == []:
                        current_json[json_rootfile] = {json_path : []}
                        appendFilepath(json_path)                          
                    elif json_rootfile in current_json and not current_json[json_rootfile] == []:
                        current_json[json_rootfile] += "," + {json_path : []}
                        appendFilepath(json_path)                         
                    if current_json is None:
                        break
        else:
            # Not only item, append to existing
            temp_obj = json_to_compare[json_rootfile]
            temp_obj[json_path] = []
            appendFilepath(json_path)             

        #print("--------------------JSON------------------")
        #print(json)
        #print("---------------------------------------")

        last_backslash_index = path.rfind(pathDelimiter)
        new_root = path[:last_backslash_index]

        # Recursively search for file paths in referenced files
        sub_parent_json_array = parent_json_array.copy()
        sub_parent_json_array.append(json_rootfile)
        find_file_paths_from_path(path, new_root, json, sub_parent_json_array, log_file, pathDelimiter, reponame)

# Check if this file is a Jenkinsfile
# Jenkinsfile contains exactly one "pipeline" keyword, any number of "agent" and "stages" followed by "{", and any number of "stage" keyword followed by "(<string>)"
def is_jenkinsfile(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

    # Define the regex patterns
    pipeline_pattern = re.compile(r'\bpipeline\s*\{')
    agent_pattern = re.compile(r'\bagent\b')
    stages_pattern = re.compile(r'\bstages\s*\{')
    stage_pattern = re.compile(r'\bstage\b\s*\(\s*["\'].*["\']\s*\)')

    # Split the content based on the stage_pattern
    stage_contents = re.split(stage_pattern, content)[1:]

    # Count the occurrences of the keywords
    pipeline_count = len(re.findall(pipeline_pattern, content))
    agent_count = len(re.findall(agent_pattern, content))
    stages_count = len(re.findall(stages_pattern, content))
    stage_count = len(re.findall(stage_pattern, content))

    # Check if the file is a Jenkinsfile based on the criteria
    if pipeline_count == 1 and agent_count >= 0 and stages_count >= 0 and stage_count >= 0:
        return stage_contents
    else:
        return None

def getStageNames(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    
    stage_pattern = re.compile(r'\bstage\b\s*\(\s*["\']([^"\']+)["\']\s*\)')
    stage_names = re.findall(stage_pattern, content)
    return stage_names


initLogFile(log_file, groovy_file_path)

# Delete all *.json and *.png files in current folder
current_folder = os.getcwd()
files_in_folder = os.listdir(current_folder)
for file in files_in_folder:
    if file.endswith('.json') or file.endswith('.png'):
        file_path = os.path.join(current_folder, file)
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")

# Find file paths recursively starting from groovy_file_path and considering repository cloned to root_repository_local_path
groovy_filepath_json = groovy_file_path.split(reponame, 1)[-1]
json_data = {
    groovy_filepath_json : []
}
parent_json_array = []


# Check if the file_path exists before trying to open it
if not os.path.exists(groovy_file_path):
    with open(log_file, "a") as f:
        f.write(groovy_file_path + "\n")
    exit

stages = is_jenkinsfile(groovy_file_path)
if stages:
    # Identify stage names
    stage_names = getStageNames(groovy_file_path)

    # Iterate through stages and populate separate json_data for each stage
    for i in range(len(stages)):
        
        stage_json = json_data.copy()
        #stage_parent_json_array = parent_json_array.copy()
        find_file_paths_in_string(stages[i], groovy_file_path, root_repository_local_path, stage_json, parent_json_array, log_file, pathDelimiter, reponame)
        
        # If the only item in stage_json is jenkinsfile, skip (no calls in a stage)
        if stage_json == json_data:
            continue

        # Check if filename unique
        new_filename = f"file_structure_{stage_names[i]}.json"
        counter = 1
        while os.path.exists(new_filename):
            new_filename = f"file_structure_{stage_names[i]}_{counter}.json"
            counter += 1
        # Save json to a file
        with open(new_filename, "w") as json_file:
            json_file.write(json.dumps(stage_json))

        # Call drawflowchart.py to draw this diagram
        try:
            # Run the other script as a subprocess and pass the filename as an argument
            subprocess.run(["python", "drawflowchart.py", new_filename], check=True)
        except subprocess.CalledProcessError as e:
            print("Error executing the subprocess:", e)

else:
    find_file_paths_from_path(groovy_file_path, root_repository_local_path, json_data, parent_json_array, log_file, pathDelimiter, reponame)

    # Save json to a file
    with open(completeJson, "w") as json_file:
        json_file.write(json.dumps(json_data))

    # Call drawflowchart.py to draw this diagram
    subprocess.run(["python", "drawflowchart.py"])