from SavConverter import sav_to_json, read_sav, json_to_sav, load_json
# imports to navigate and manipulate the json structure
from SavConverter import obj_to_json, print_json, get_object_by_path, insert_object_by_path, replace_object_by_path, update_property_by_path

# The following lines are an example of the .sav to .json conversion process


res = read_sav("./SAOFBS/SaveData.sav")
jsonO = sav_to_json(res, string=True)

with open("output.json", "w") as f:
    f.write(jsonO)