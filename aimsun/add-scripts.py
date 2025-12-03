import os

folder_path = r"C:\Users\caleb\OneDrive - Mobility Lab Limited\General - Projects\1025 - New North Road Aimsun\Model\Resources\Scripts"
script_externalid = 'test'

script_type = model.getType("GKScript")

# Get or create the "Scripts" folder in the model ===
folder_name = "GKModel::top::scripts"
root_folder = model.getCreateRootFolder()
scripts_folder = root_folder.findFolder(folder_name)
if scripts_folder is None:
    scripts_folder = GKSystem.getSystem().createFolder(root_folder, folder_name)

for filename in os.listdir(folder_path):
    if filename.endswith(".py"):
        filepath = os.path.join(folder_path, filename)

        # Check if a script with the same name already exists
        existing_script = None
        for s in model.getCatalog().getObjectsByType(script_type).values():
            if s.getName() == os.path.splitext(filename)[0]:
                existing_script = s
                break

        if existing_script is None:
            # Create new GKScript object
            script_obj = GKSystem.getSystem().newObject("GKScript", model)
            script_obj.setName(os.path.splitext(filename)[0])
            scripts_folder.append(script_obj)
        else:
            script_obj = existing_script

        # Set the script to reference the external file
        script_obj.setFileName(filepath)
        script_obj.setExternalId(script_externalid)


model.getCommander().addCommand(None)

print("External script links have been added/updated in the Aimsun model.")
