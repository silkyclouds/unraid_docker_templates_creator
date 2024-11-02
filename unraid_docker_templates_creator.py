import json
import xml.etree.ElementTree as ET
import os
import shutil
import subprocess

def create_xml_from_json(json_file, xml_file):
    """Converts a JSON file to an XML file for Unraid templates."""
    with open(json_file, 'r') as f:
        data = json.load(f)

    container_data = data[0]  # Access the first (and only) item in the list

    # Create the XML structure
    container = ET.Element('Container')

    # Fill in the necessary information
    name = ET.SubElement(container, 'Name')
    name.text = container_data['Name'].strip('/')  # Use the name of the container without leading slash

    description = ET.SubElement(container, 'Description')
    description.text = "Description of the container functionality goes here."

    registry = ET.SubElement(container, 'Registry')
    registry.text = f"https://registry.hub.docker.com/u/{container_data['Config']['Image'].split('/')[1]}/"

    repository = ET.SubElement(container, 'Repository')
    repository.text = container_data['Config']['Image']

    bind_time = ET.SubElement(container, 'BindTime')
    bind_time.text = "true"

    privileged = ET.SubElement(container, 'Privileged')
    privileged.text = "false"

    # Networking
    networking = ET.SubElement(container, 'Networking')
    mode = ET.SubElement(networking, 'Mode')
    mode.text = "bridge"

    publish = ET.SubElement(networking, 'Publish')
    container_port = None  # Initialize container_port to avoid UnboundLocalError
    for port, bindings in container_data['HostConfig']['PortBindings'].items():
        for binding in bindings:
            port_elem = ET.SubElement(publish, 'Port')
            host_port = ET.SubElement(port_elem, 'HostPort')
            host_port.text = binding['HostPort']
            container_port = port.split('/')[0]  # Extract the port number
            container_port_elem = ET.SubElement(port_elem, 'ContainerPort')
            container_port_elem.text = container_port  # Set container port
            protocol = ET.SubElement(port_elem, 'Protocol')
            protocol.text = port.split('/')[1]  # Extract the protocol (tcp/udp)

    # Data
    data_elem = ET.SubElement(container, 'Data')
    for mount in container_data['Mounts']:
        if mount['Type'] == "bind":
            volume_elem = ET.SubElement(data_elem, 'Volume')
            host_dir = ET.SubElement(volume_elem, 'HostDir')
            host_dir.text = mount['Source']
            container_dir = ET.SubElement(volume_elem, 'ContainerDir')
            container_dir.text = mount['Destination']
            mode_elem = ET.SubElement(volume_elem, 'Mode')
            mode_elem.text = "rw"

    # Environment Variables
    env_elem = ET.SubElement(container, 'Environment')
    for env in container_data['Config']['Env']:
        if '=' in env:
            parts = env.split('=')
            if len(parts) == 2:  # Check if there are exactly 2 parts
                env_name = parts[0]
                env_value = parts[1]
                variable_elem = ET.SubElement(env_elem, 'Variable')
                name_elem = ET.SubElement(variable_elem, 'Name')
                name_elem.text = env_name
                value_elem = ET.SubElement(variable_elem, 'Value')
                value_elem.text = env_value
            else:
                print(f"Warning: Skipping malformed environment variable entry: {env}")
        else:
            print(f"Warning: No '=' found in environment variable entry: {env}")

    # Version
    version = ET.SubElement(container, 'Version')
    version.text = "latest"

    # Additional optional elements
    web_ui = ET.SubElement(container, 'WebUI')
    web_ui.text = f"http://[IP]:[PORT:{container_port}]/" if container_port else "http://[IP]:[PORT]/"

    banner = ET.SubElement(container, 'Banner')
    banner.text = "http://example.com/path/to/banner.png"  # Placeholder for banner URL

    icon = ET.SubElement(container, 'Icon')
    icon.text = "http://example.com/path/to/icon.png"  # Placeholder for icon URL

    extra_params = ET.SubElement(container, 'ExtraParams')
    extra_params.text = ""

    # Save the XML file
    tree = ET.ElementTree(container)
    tree.write(xml_file, encoding='utf-8', xml_declaration=True)
    print(f"XML file created: {xml_file}")

def validate_json_file(json_file):
    """Checks if the JSON file is valid and contains expected keys."""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        if isinstance(data, list) and 'Name' in data[0] and 'Config' in data[0]:
            return True
    except (json.JSONDecodeError, IndexError):
        return False
    return False

def validate_xml_file(xml_file):
    """Checks if the XML file is valid."""
    try:
        with open(xml_file, 'r') as f:
            ET.parse(f)  # Parse the XML file to validate
        return True
    except ET.ParseError:
        return False

def docker_inspect(container_id):
    """Runs docker inspect and returns the output in JSON format."""
    try:
        result = subprocess.run(['docker', 'inspect', container_id], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error inspecting container {container_id}: {e}")
        return None

def get_running_containers():
    """Retrieves a list of running containers."""
    try:
        result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], capture_output=True, text=True, check=True)
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error fetching running containers: {e}")
        return []

def get_non_running_containers():
    """Retrieves a list of non-running containers."""
    try:
        result = subprocess.run(['docker', 'ps', '-a', '--format', '{{.Names}}'], capture_output=True, text=True, check=True)
        return [name for name in result.stdout.splitlines() if name not in get_running_containers()]
    except subprocess.CalledProcessError as e:
        print(f"Error fetching non-running containers: {e}")
        return []

def main():
    # Ask if the user wants to create JSONs from docker inspect
    create_jsons = input("Do you want to create JSONs from docker inspect? (y/n): ")
    
    if create_jsons.lower() == 'y':
        # Process running containers
        running_containers = get_running_containers()
        print("Running Containers:")
        for container in running_containers:
            print(f"  - {container}")
        
        if running_containers:
            create_json_running = input("Do you want to create JSON files for the running containers? (y/n): ")
            if create_json_running.lower() == 'y':
                for container in running_containers:
                    json_file_name = f"{container}.json"
                    json_file_path = os.path.join('/mnt/cache/appdata/scripts', json_file_name)
                    json_output = docker_inspect(container)
                    if json_output:
                        with open(json_file_path, 'w') as json_file:
                            json_file.write(json_output)
                        print(f"Created JSON file for {container}: {json_file_path}")

        # Process non-running containers
        non_running_containers = get_non_running_containers()
        print("Non-Running Containers:")
        for container in non_running_containers:
            print(f"  - {container}")
        
        if non_running_containers:
            create_json_non_running = input("Do you want to create JSON files for the non-running containers? (y/n): ")
            if create_json_non_running.lower() == 'y':
                for container in non_running_containers:
                    json_file_name = f"{container}.json"
                    json_file_path = os.path.join('/mnt/cache/appdata/scripts', json_file_name)
                    json_output = docker_inspect(container)
                    if json_output:
                        with open(json_file_path, 'w') as json_file:
                            json_file.write(json_output)
                        print(f"Created JSON file for {container}: {json_file_path}")

    # Convert JSON files to XML
    folder_path = input("Enter the path to the folder with JSON files (default: /mnt/cache/appdata/scripts): ") or '/mnt/cache/appdata/scripts'
    
    if not os.path.exists(folder_path):
        print("Invalid folder path. Exiting.")
        return

    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    
    total_files = len(json_files)
    print(f"Total JSON files found: {total_files}")
    print("JSON Files:")
    for json_file in json_files:
        print(f"  - {json_file}")

    valid_files = []

    for json_file in json_files:
        full_path = os.path.join(folder_path, json_file)
        if validate_json_file(full_path):
            valid_files.append(full_path)
        else:
            print(f"Invalid JSON file: {json_file}")

    if valid_files:
        convert_choice = input("Do you want to convert all valid JSON files? (y/n): ")
        if convert_choice.lower() == 'y':
            xml_files_created = []
            for json_file_path in valid_files:
                xml_file_name = os.path.splitext(os.path.basename(json_file_path))[0] + '.xml'
                xml_file_path = os.path.join(folder_path, xml_file_name)
                create_xml_from_json(json_file_path, xml_file_path)
                if validate_xml_file(xml_file_path):
                    print(f"Valid XML created: {xml_file_path}")
                    xml_files_created.append(xml_file_path)
                else:
                    print(f"Invalid XML created: {xml_file_path}")

            move_choice = input("Do you want to move XML files to Unraid's templates-user folder? (y/n): ")
            if move_choice.lower() == 'y':
                templates_user_folder = '/boot/config/plugins/dockerMan/templates-user/'
                for xml_file in xml_files_created:
                    try:
                        shutil.move(xml_file, templates_user_folder)
                        print(f"Moved {xml_file} to {templates_user_folder}")
                    except Exception as e:
                        print(f"Failed to move {xml_file}: {e}")

            # Display statistics
            print(f"Total JSON files processed: {total_files}")
            print(f"Total valid XML files created: {len(xml_files_created)}")
            print(f"XML files moved to Unraid template folder: {len(xml_files_created) if move_choice.lower() == 'y' else 0}")

if __name__ == "__main__":
    main()
