import os
import subprocess
import docker
import tkinter as tk
from tkinter import messagebox, filedialog

# Docker client setup
docker_client = docker.from_env()


# Utility functions
def run_command(command):
    """Runs a shell command and returns the output."""
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e.stderr}")
        return None


# Feature Implementations

def create_vm(cpu, memory, disk, name):
    command = [
        "qemu-img", "create", f"{name}.qcow2", f"{disk}G"
    ]
    if run_command(command):
        print(f"Disk {name}.qcow2 created successfully.")

    command = [
        "qemu-system-x86_64",
        "-cpu", f"{cpu}", "-m", f"{memory}", "-hda", f"{name}.qcow2"
    ]
    subprocess.Popen(command)


def create_dockerfile(path, content):
    try:
        with open(os.path.join(path, "Dockerfile"), 'w') as file:
            file.write("\n".join(content))
        return True
    except Exception as e:
        print(f"Error creating Dockerfile: {e}")
        return False


def build_docker_image(dockerfile_path, image_name):
    try:
        docker_client.images.build(path=dockerfile_path, tag=image_name)
        return True
    except Exception as e:
        print(f"Error building image: {e}")
        return False


def list_docker_images():
    return [image.tags for image in docker_client.images.list()]


def list_running_containers():
    return [(container.id, container.name, container.status) for container in docker_client.containers.list()]


def stop_container(container_id):
    try:
        container = docker_client.containers.get(container_id)
        container.stop()
        return True
    except Exception as e:
        print(f"Error stopping container: {e}")
        return False


def search_image(image_name):
    return [image.tags for image in docker_client.images.list() if image_name in image.tags]


def search_dockerhub(image_name):
    command = ["docker", "search", image_name]
    return run_command(command)


def pull_image(image_name):
    try:
        docker_client.images.pull(image_name)
        return True
    except Exception as e:
        print(f"Error pulling image: {e}")
        return False


# GUI Application
def main():
    root = tk.Tk()
    root.title("Cloud Management System")

    def vm_create():
        cpu = cpu_entry.get()
        memory = memory_entry.get()
        disk = disk_entry.get()
        name = vm_name_entry.get()
        create_vm(cpu, memory, disk, name)
        messagebox.showinfo("Success", "VM Created Successfully")

    def dockerfile_create():
        path = filedialog.askdirectory(title="Select Path to Save Dockerfile")
        content = text_editor.get("1.0", tk.END).strip().split("\n")
        if create_dockerfile(path, content):
            messagebox.showinfo("Success", "Dockerfile Created Successfully")

    def docker_image_build():
        path = filedialog.askdirectory(title="Select Path to Dockerfile")
        name = docker_image_name_entry.get()
        if build_docker_image(path, name):
            messagebox.showinfo("Success", "Docker Image Built Successfully")

    def show_images():
        images = list_docker_images()
        images_list.delete(0, tk.END)
        for image in images:
            images_list.insert(tk.END, image)

    def show_containers():
        containers = list_running_containers()
        containers_list.delete(0, tk.END)
        for c in containers:
            containers_list.insert(tk.END, f"ID: {c[0]}, Name: {c[1]}, Status: {c[2]}")

    def stop_selected_container():
        selected = containers_list.get(containers_list.curselection())
        container_id = selected.split(",")[0].split(": ")[1]
        if stop_container(container_id):
            messagebox.showinfo("Success", "Container Stopped")

    # VM Frame
    vm_frame = tk.LabelFrame(root, text="Create VM")
    vm_frame.pack(fill="both", expand=True, padx=10, pady=5)

    tk.Label(vm_frame, text="CPU").grid(row=0, column=0, padx=5, pady=5)
    cpu_entry = tk.Entry(vm_frame)
    cpu_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(vm_frame, text="Memory (MB)").grid(row=1, column=0, padx=5, pady=5)
    memory_entry = tk.Entry(vm_frame)
    memory_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(vm_frame, text="Disk (GB)").grid(row=2, column=0, padx=5, pady=5)
    disk_entry = tk.Entry(vm_frame)
    disk_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(vm_frame, text="VM Name").grid(row=3, column=0, padx=5, pady=5)
    vm_name_entry = tk.Entry(vm_frame)
    vm_name_entry.grid(row=3, column=1, padx=5, pady=5)

    tk.Button(vm_frame, text="Create VM", command=vm_create).grid(row=4, columnspan=2, pady=10)

    # Dockerfile Frame
    dockerfile_frame = tk.LabelFrame(root, text="Dockerfile")
    dockerfile_frame.pack(fill="both", expand=True, padx=10, pady=5)

    text_editor = tk.Text(dockerfile_frame, height=10)
    text_editor.pack(fill="both", padx=5, pady=5)

    tk.Button(dockerfile_frame, text="Create Dockerfile", command=dockerfile_create).pack(pady=5)

    # Docker Images Frame
    images_frame = tk.LabelFrame(root, text="Docker Images")
    images_frame.pack(fill="both", expand=True, padx=10, pady=5)

    images_list = tk.Listbox(images_frame, height=10)
    images_list.pack(fill="both", padx=5, pady=5)

    tk.Button(images_frame, text="List Images", command=show_images).pack(pady=5)

    # Containers Frame
    containers_frame = tk.LabelFrame(root, text="Running Containers")
    containers_frame.pack(fill="both", expand=True, padx=10, pady=5)

    containers_list = tk.Listbox(containers_frame, height=10)
    containers_list.pack(fill="both", padx=5, pady=5)

    tk.Button(containers_frame, text="List Containers", command=show_containers).pack(pady=5)
    tk.Button(containers_frame, text="Stop Container", command=stop_selected_container).pack(pady=5)

    # Docker Image Build Frame
    docker_image_frame = tk.LabelFrame(root, text="Build Docker Image")
    docker_image_frame.pack(fill="both", expand=True, padx=10, pady=5)

    tk.Label(docker_image_frame, text="Image Name").grid(row=0, column=0, padx=5, pady=5)
    docker_image_name_entry = tk.Entry(docker_image_frame)
    docker_image_name_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Button(docker_image_frame, text="Build Image", command=docker_image_build).grid(row=1, columnspan=2, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
