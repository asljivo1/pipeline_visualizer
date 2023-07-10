import os
import json
import re
import subprocess

def initLogFile(log_file, jenkinsfile):
    with open(log_file, "a") as f:
            f.write("===========================================================\n")
            f.write(f"Missing files in tree with root '{jenkinsfile}':" + "\n")
            f.write("===========================================================\n")

def find_file_paths(file_path, root_path, json, parent_json_array, log_file):
    print(f"Called find_file_paths for file_path={file_path} and root=<{root_path}>")

    # Check if the file_path exists before trying to open it
    if not os.path.exists(file_path):
        with open(log_file, "a") as f:
            f.write(file_path + "\n")
        return

    #file_paths = []
    with open(file_path, 'r') as file:
        content = file.read()

        # Search for file paths with extensions '.bat' and '.py'
        paths = re.findall(r'[\'"]([^\'"\s]*\.(bat|py|mmf))', content)


        # Replace '/' with '\'
        paths = [path[0].replace('/', '\\') for path in paths]
        print(f"PATHS=<{paths}>--------------")
        # Process each found file path
        for path in paths:
            # Remove '%~dp0' from the beginning of the string if present
            if path.startswith("%~dp0"):
                path = path.replace("%~dp0", "", 1)

            if path.find(root_path) == -1:
                # not found
                print(f"path <{path}> does not contain root_path {root_path}. Contencate!")
                if path.count('..') > 0:
                    # Count occurrences of '..' in the path
                    N = path.count('..')

                    # Remove part of the string from last Nth backslash until the end
                    path_parts = root_path.split('\\')
                    new_root_path = '\\'.join(path_parts[:-N]) if N > 0 else root_path

                    path_parts = path.split('\\')
                    new_path = '\\'.join(path_parts[N:]) if N > 0 else path

                    # Concatenate the new path with the root path
                    path = os.path.join(new_root_path, new_path)
                else:
                    path = root_path + '\\' + path

            print(f"new path={path}")
            #file_paths.append(path) NOT NEEDED?

            # TODO Add this path to json
            # Check if the key exists and its value is an array
            reponame = "aa-sca---uwb-sw---rom\\"
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
                #json[json_rootfile] = {json_path : []}
                # Traverse the parent_json_array and access the nested JSON values
                if not parent_json_array:
                    if json[json_rootfile] == []:
                        json[json_rootfile] = {json_path : []}
                    else:
                        print("HERE")
                else:
                    current_json = json
                    for key in parent_json_array:
                        current_json = current_json[key]
                        if json_rootfile in current_json and current_json[json_rootfile] == []:
                            current_json[json_rootfile] = {json_path : []}
                        elif json_rootfile in current_json and not current_json[json_rootfile] == []:
                            current_json[json_rootfile] += "," + {json_path : []}
                        if current_json is None:
                            break
            else:
                # Not only item, append t existing
                #current_json[json_rootfile] += "," + {json_path : []}
                temp_obj = json_to_compare[json_rootfile]
                temp_obj[json_path] = []

            print("--------------------JSON------------------")
            print(json)
            print("---------------------------------------")
            # Update root_path
            # Find the index of the last backslash
            last_backslash_index = path.rfind('\\')
            # Extract the substring from the start until the last backslash
            new_root = path[:last_backslash_index]

            # Recursively search for file paths in referenced files
            sub_parent_json_array = parent_json_array.copy()
            sub_parent_json_array.append(json_rootfile)
            #sub_file_paths = find_file_paths(path, new_root, json, sub_parent_json_array, log_file)
            find_file_paths(path, new_root, json, sub_parent_json_array, log_file)
            #if sub_file_paths:
            #    print(f"sub_file_paths={sub_file_paths}")
            #    file_paths.extend(sub_file_paths)

    #return file_paths

# def create_file_structure(file_paths):
#     file_structure = {}
#     for path in file_paths:
#         dir_name, file_name = os.path.split(path)
#         if file_name not in file_structure:
#             file_structure[file_name] = {}
        
#         if dir_name:
#             dir_structure = create_file_structure([dir_name])
#             file_structure[file_name] = dir_structure

#     return file_structure

# Specify the Jenkinsfile file path
root_repository_local_path = r"C:\Users\aseferagic\OneDrive - ENDAVA\Work\NXP Ranger5 July 2023\ROM-repo\aa-sca---uwb-sw---rom"
groovy_file_path = r"C:\Users\aseferagic\OneDrive - ENDAVA\Work\NXP Ranger5 July 2023\ROM-repo\aa-sca---uwb-sw---rom\onic\ROM\toolsupport\jenkinsfile"
#groovy_file_path = os.path.join("C:", "Users", user, "OneDrive - ENDAVA", folder, "NXP Ranger5 July 2023", "build", "build", file_name)

log_file = "missing_files.txt"
initLogFile(log_file, groovy_file_path)

# Find file paths recursively starting from groovy_file_path and considering repository cloned to root_repository_local_path
reponame = "aa-sca---uwb-sw---rom\\"
groovy_filepath_json = groovy_file_path.split(reponame, 1)[-1]
json_data = {
    groovy_filepath_json : []
}
parent_json_array = []
file_paths = find_file_paths(groovy_file_path, root_repository_local_path, json_data, parent_json_array, log_file)

# Create the file structure
#file_structure = create_file_structure(file_paths)

# Convert the file structure to JSON
#json_data = json.dumps(file_structure, indent=4)

# Print or save the JSON structure
print(json_data)
# Or save it to a file
with open("file_structure.json", "w") as json_file:
    json_file.write(json.dumps(json_data))

# Call drawflowchart.py to draw this diagram
subprocess.run(["python", "drawflowchart.py"])