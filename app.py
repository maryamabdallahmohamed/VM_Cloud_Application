import subprocess
import tkinter as tk
from tkinter import BOTH, filedialog, messagebox, simpledialog
import requests
import customtkinter as ctk
import os

class DesktopApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Set consistent color scheme
        self.GREEN_DARK = '#135E4B'
        self.GREEN_LIGHT = '#4CB572'
        self.GREEN_HOVER = '#A1D8B5'
        
        # Configure window
        self.title("Cloud Management System")
        self.geometry("1200x800")
        self.configure(fg_color=self.GREEN_LIGHT)
    
        # VM Configuration Variables
        self.cpu_var = ctk.StringVar(value="1")
        self.memory_var = ctk.StringVar(value="1024")
        self.disk_var = ctk.StringVar()
        
        # Docker-related Variables
        self.dockerfile_path_var = ctk.StringVar()
        self.docker_image_name_var = ctk.StringVar()

        # # Create a consistent style for buttons
        # self.ctk.CTkButton.configure(self, 
        #                         fg_color=self.GREEN_DARK, 
        #                         hover_color=self.GREEN_HOVER, 
        #                         text_color='white', 
        #                         corner_radius=10)

        # Create main UI
        self.create_main_interface()

    def create_main_interface(self):
        """Create the main interface with consistent layout"""
        # Left-side option frame with fixed width
        self.option_frame = ctk.CTkFrame(self, 
                                         width=200,  # Increased width for consistency
                                         height=800,  
                                         fg_color=self.GREEN_DARK,
                                         corner_radius=10)
        self.option_frame.pack(side=ctk.LEFT, fill=ctk.Y, padx=10, pady=10)
        self.option_frame.pack_propagate(False)  # Prevent frame from resizing

        # Create buttons for different sections with consistent styling
        sections = [
            ("Virtual Machines", self.show_vm_section),
            ("Docker Files", self.show_docker_files_section),
            ("Docker Hub", self.show_docker_hub_section),
            ("Manage Containers", self.show_containers_section),
            ("Build Docker Image", self.build_docker_image),
            ("Stop Container", self.stop_docker_container),
            ("Search Image", self.search_local_image),
            ("Pull Docker Image", self.pull_docker_image),

        ]

        for text, command in sections:
            btn = ctk.CTkButton(self.option_frame, 
                                text=text, 
                                command=command,
                                width=180,  # Consistent button width
                                height=40)  # Consistent button height
            btn.pack(pady=10)

        # Right-side main content frame with fixed width
        self.main_frame = ctk.CTkFrame(self, 
                                       fg_color=self.GREEN_LIGHT, 
                                       width=950,  # Calculated width
                                       height=800)
        self.main_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        self.main_frame.pack_propagate(False)  # Prevent frame from resizing

        # Initially show VM section
        self.show_vm_section()
    def show_vm_section(self):
        """Display Virtual Machine configuration section"""
        # Clear previous content
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # VM Configuration Frame
        vm_frame = ctk.CTkFrame(self.main_frame, bg_color='#4CB572', fg_color='#4CB572')
        vm_frame.pack(expand=True, fill=ctk.BOTH, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(vm_frame, text="Virtual Machine Configuration", 
                                font=('Helvetica', 16, 'bold'))
        title_label.pack(pady=10)

        # Configuration Inputs
        config_frame = ctk.CTkFrame(vm_frame, bg_color='#4CB572', fg_color='#4CB572')
        config_frame.pack(expand=True)

        # CPU Configuration
        cpu_label = ctk.CTkLabel(config_frame, text="Number of CPUs:",font=('Helvetica', 16, 'bold'))
        cpu_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        cpu_entry = ctk.CTkEntry(config_frame, textvariable=self.cpu_var, width=120)
        cpu_entry.grid(row=0, column=2, padx=5, pady=5,sticky='w')

        # Memory Configuration
        memory_label = ctk.CTkLabel(config_frame, text="Memory (MB):",font=('Helvetica', 16, 'bold'))
        memory_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')
        memory_entry = ctk.CTkEntry(config_frame, textvariable=self.memory_var, width=120)
        memory_entry.grid(row=1, column=2, padx=5, pady=5,sticky='w')

        # Disk Image Configuration
        disk_label =ctk.CTkLabel(config_frame, text="Disk Image Path:", font=('Helvetica', 16, 'bold'))
        disk_label.grid(row=2, column=0, padx=5, pady=5, sticky='e')
        disk_entry = ctk.CTkEntry(config_frame, textvariable=self.disk_var, width=120)
        disk_entry.grid(row=2, column=2, padx=5, pady=5,sticky='w')
        
        # Browse Disk Button
        browse_btn = ctk.CTkButton(config_frame, text="Browse", command=self.browse_disk,
                                   bg_color='#135E4B',fg_color='#135E4B',hover_color='#A1D8B5',
                                   background_corner_colors=(['#135E4B','#135E4B','#135E4B','#135E4B']),
                                   corner_radius=30,width=70)
        browse_btn.grid(row=4, column=2, padx=5, pady=5)

        # Create VM Button
        create_vm_btn = ctk.CTkButton(vm_frame, text="Create Virtual Machine", 
                                  command=self.create_vm,bg_color='#135E4B',fg_color='#135E4B',hover_color='#A1D8B5',
                                   background_corner_colors=(['#135E4B','#135E4B','#135E4B','#135E4B']),
                                   corner_radius=30)
        create_vm_btn.pack(pady=10)

        # VM List Frame
        list_frame = ctk.CTkFrame(vm_frame, bg_color='#4CB572', fg_color='#4CB572')
        list_frame.pack(expand=True, fill=ctk.BOTH, padx=10, pady=10)

        # VM List Label
        list_label = ctk.CTkLabel(list_frame, text="Existing Virtual Machines")
        list_label.pack()

        # VM Listbox
        self.vm_listbox =tk.Listbox(list_frame, width=50, height=10)
        self.vm_listbox.pack(expand=True, fill=ctk.BOTH)

        # Refresh VM List Button
        refresh_btn = ctk.CTkButton(vm_frame, text="Refresh VM List", command=self.list_vms,bg_color='#135E4B',fg_color='#135E4B',hover_color='#A1D8B5',
                                   background_corner_colors=(['#135E4B','#135E4B','#135E4B','#135E4B']),
                                   corner_radius=30)
        refresh_btn.pack(pady=5)

    def browse_disk(self):
        """Open file dialog to select disk image"""
        file_path = filedialog.askopenfilename(
            title="Select Disk Image",
            filetypes=(("Disk Images", "*.qcow2 *.img *.iso"), ("All Files", "*.*"))
        )
        if file_path:
            self.disk_var.set(file_path)

    def create_vm(self):
        """Create a new virtual machine using QEMU"""
        try:
            # Validate inputs
            cpu = int(self.cpu_var.get())
            memory = int(self.memory_var.get())
            disk = self.disk_var.get()

            # Validate disk image
            if not os.path.exists(disk):
                messagebox.showerror("Error", "Disk image file does not exist!")
                return

            # Prepare QEMU command
            qemu_cmd = [
                "qemu-system-x86_64",
                f"-smp", str(cpu),
                f"-m", str(memory),
                f"-drive", f"file={disk},format=qcow2" if disk.endswith(".qcow2") else f"file={disk},format=raw",
                "-vga", "virtio",
                "-net", "nic",
                "-net", "user"
            ]

            # Launch VM
            subprocess.Popen(qemu_cmd)
            messagebox.showinfo("Success", "Virtual machine launched!")

            # Refresh VM list
            self.list_vms()

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for CPU and memory.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def list_vms(self):
        """List existing virtual machines"""
        self.vm_listbox.delete(0, ctk.END)
        try:
            # This is a simplified VM listing - you might need to adjust based on your specific VM management
            result = subprocess.run(["virsh", "list", "--all"], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')[2:]  # Skip header lines
            
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        self.vm_listbox.insert(ctk.END, f"ID: {parts[0]}, Name: {parts[1]}, State: {parts[2]}")
        except subprocess.CalledProcessError:
            messagebox.showwarning("Warning", "Unable to list VMs. Is virtualization management tool installed?")
        except FileNotFoundError:
            messagebox.showerror("Error", "Virtualization management tool not found.")

    def show_docker_files_section(self):
        """Display Docker Files section"""
        # Clear previous content
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Docker Files Frame
        docker_frame = ctk.CTkFrame(self.main_frame,  bg_color='#4CB572', fg_color='#4CB572')
        docker_frame.pack(expand=True, fill=ctk.BOTH, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(docker_frame, text="Docker Files Management", 
                                font=('Helvetica', 16, 'bold'))
        title_label.pack(pady=10)

        # Dockerfile Creation Section
        create_frame = ctk.CTkFrame(docker_frame, bg_color='#4CB572', fg_color='#4CB572')
        create_frame.pack(fill=ctk.BOTH ,padx=10, pady=10)

        # Dockerfile Path
        path_label = ctk.CTkLabel(create_frame, text="Dockerfile Path:")
        path_label.pack(side=ctk.LEFT, padx=5)
        path_entry = tk.Entry(create_frame, textvariable=self.dockerfile_path_var, width=50)
        path_entry.pack(side=ctk.LEFT, padx=5)
        browse_btn = ctk.CTkButton(create_frame, text="Browse", command=self.set_dockerfile_path,bg_color='#135E4B',fg_color='#135E4B',hover_color='#A1D8B5',
                                   background_corner_colors=(['#135E4B','#135E4B','#135E4B','#135E4B']),
                                   corner_radius=30,width=70)
        browse_btn.pack(side=ctk.LEFT, padx=5)

        # Create Dockerfile Button
        create_btn = ctk.CTkButton(docker_frame, text="Create Dockerfile", command=self.create_dockerfile,
                                    bg_color='#135E4B',fg_color='#135E4B',hover_color='#A1D8B5',
                                   background_corner_colors=(['#135E4B','#135E4B','#135E4B','#135E4B']),
                                   corner_radius=30,width=70)
        create_btn.pack(pady=10)

    def set_dockerfile_path(self):
        """Set path for Dockerfile"""
        path = filedialog.askdirectory(title="Select Dockerfile Save Location")
        if path:
            self.dockerfile_path_var.set(os.path.join(path, "Dockerfile"))

    def create_dockerfile(self):
        """Create a new Dockerfile"""
        save_path = self.dockerfile_path_var.get()
        if not save_path:
            messagebox.showerror("Error", "Please specify a path to save the Dockerfile.")
            return

        # Prompt for Dockerfile content
        base_image = simpledialog.askstring("Base Image", "Enter base image (e.g., python:3.9):")
        commands = simpledialog.askstring("Commands", "Enter commands (one per line):")

        # Generate Dockerfile content
        dockerfile_content = f"FROM {base_image or 'ubuntu:latest'}\n"
        if commands:
            for cmd in commands.split('\n'):
                dockerfile_content += f"RUN {cmd}\n"

        try:
            with open(save_path, "w") as f:
                f.write(dockerfile_content)
            messagebox.showinfo("Success", f"Dockerfile created at {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create Dockerfile: {str(e)}")

    def show_docker_hub_section(self):
        """Display Docker Hub section"""
        # Clear previous content
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Docker Hub Frame
        hub_frame = ctk.CTkFrame(self.main_frame, bg_color='#4CB572', fg_color='#4CB572')
        hub_frame.pack(expand=True, fill=ctk.BOTH, padx=20, pady=20)

        # Search Frame
        search_frame = ctk.CTkFrame(hub_frame,  bg_color='#4CB572', fg_color='#4CB572')
        search_frame.pack(fill=ctk.X, padx=10, pady=10)

        # Search Entry
        search_label = ctk.CTkLabel(search_frame, text="Search Docker Hub:")
        search_label.pack(side=ctk.LEFT, padx=5)
        search_entry = tk.Entry(search_frame, width=50)
        search_entry.pack(side=ctk.LEFT, padx=5)

        # Search Button
        search_btn = ctk.CTkButton(search_frame, text="Search", 
                                command=lambda: self.search_docker_hub(search_entry.get()),bg_color='#135E4B',fg_color='#135E4B',hover_color='#A1D8B5',
                                   background_corner_colors=(['#135E4B','#135E4B','#135E4B','#135E4B']),
                                   corner_radius=30,width=70)
        search_btn.pack(side=ctk.LEFT, padx=5)

        # Results Listbox
        self.docker_hub_listbox = tk.Listbox(hub_frame, width=70, height=20)
        self.docker_hub_listbox.pack(expand=True, fill=ctk.BOTH, padx=10, pady=10)

    def search_docker_hub(self, query):
        """Search Docker Hub for images"""
        self.docker_hub_listbox.delete(0, tk.END)
        try:
            response = requests.get(f"https://hub.docker.com/v2/search/repositories/?query={query}")
            response.raise_for_status()
            results = response.json().get('results', [])
            
            for result in results:
                self.docker_hub_listbox.insert(tk.END, 
                    f"{result.get('repo_name', 'N/A')} - Stars: {result.get('star_count', 0)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search Docker Hub: {str(e)}")

    def show_containers_section(self):
        """Display Containers Management section"""
        # Clear previous content
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Containers Frame
        containers_frame = ctk.CTkFrame(self.main_frame, bg_color='#4CB572', fg_color='#4CB572')
        containers_frame.pack(expand=True, fill=ctk.BOTH, padx=20, pady=20)

        # Buttons Frame
        btn_frame = ctk.CTkFrame(containers_frame,  bg_color='#4CB572', fg_color='#4CB572')
        btn_frame.pack(fill=ctk.X, padx=10, pady=10)

        # List Images Button
        list_images_btn = ctk.CTkButton(btn_frame, text="List Docker Images", 
                                    command=self.list_docker_images,
                                    bg_color='#135E4B',fg_color='#135E4B',hover_color='#A1D8B5',
                                   background_corner_colors=(['#135E4B','#135E4B','#135E4B','#135E4B']),
                                   corner_radius=30,width=70)
        list_images_btn.pack(side=ctk.LEFT, padx=5)

        # List Containers Button
        list_containers_btn = ctk.CTkButton(btn_frame, text="List Docker Containers", 
                                command=self.list_docker_containers,
                                bg_color='#135E4B',fg_color='#135E4B',hover_color='#A1D8B5',
                                background_corner_colors=(['#135E4B','#135E4B','#135E4B','#135E4B']),
                                corner_radius=30,width=70)
        list_containers_btn.pack(side=ctk.LEFT, padx=5)

        # Listboxes
        list_frame = ctk.CTkFrame(containers_frame)
        list_frame.pack(expand=True, fill=ctk.BOTH, padx=10, pady=10)

        # Images Listbox
        images_label = ctk.CTkLabel(list_frame, text="Docker Images:")
        images_label.pack()
        self.images_listbox = tk.Listbox(list_frame, width=70, height=10)
        self.images_listbox.pack(expand=True, fill=ctk.BOTH)

        # Containers Listbox
        containers_label = ctk.CTkLabel(list_frame, text="Docker Containers:")
        containers_label.pack()
        self.containers_listbox = tk.Listbox(list_frame, width=70, height=10)
        self.containers_listbox.pack(expand=True, fill=ctk.BOTH)

    def list_docker_images(self):
        """List all Docker images on the system"""
        self.images_listbox.delete(0, tk.END)
        try:
            result = subprocess.run(["docker", "images"], capture_output=True, text=True, check=True)
            output = result.stdout.strip().split('\n')
            
            for line in output[1:]:  # Skip header
                columns = line.split()
                if columns:
                    self.images_listbox.insert(tk.END, f"{columns[0]}:{columns[1]}")
            
            messagebox.showinfo("Success", "Docker images listed successfully!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to list Docker images: {str(e)}")
        except FileNotFoundError:
            messagebox.showerror("Error", "Docker is not installed or not in PATH.")

    def list_docker_containers(self):
        """List all Docker containers on the system"""
        self.containers_listbox.delete(0, tk.END)
        try:
            result = subprocess.run(["docker", "ps", "-a"], capture_output=True, text=True, check=True)
            output = result.stdout.strip().split('\n')
            
            for line in output[1:]:  # Skip header
                columns = line.split()
                if columns:
                    self.containers_listbox.insert(ctk.END, f"{columns[0]} - {columns[-1]}")
            
            messagebox.showinfo("Success", "Docker containers listed successfully!")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to list Docker containers: {str(e)}")
        except FileNotFoundError:
            messagebox.showerror("Error", "Docker is not installed or not in PATH.")

    def stop_selected_container(self):
        """Stop the selected Docker container"""
        try:
            selection = self.containers_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a container to stop.")
                return

            container_id = self.containers_listbox.get(selection[0]).split()[0]
            subprocess.run(["docker", "stop", container_id], check=True)
            
            messagebox.showinfo("Success", f"Container {container_id} stopped successfully!")
            self.list_docker_containers()  # Refresh the list
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to stop container: {str(e)}")

    def download_image(self):
        """Download a Docker image from Docker Hub based on user input."""
        image_name = self.search_entry.get().strip()
        if not image_name:
            messagebox.showwarning("Input Error", "Please enter an image name to download.")
            return
        
        try:
            # Run the docker pull command
            result = subprocess.run(['docker', 'pull', image_name], capture_output=True, text=True)
            
            if result.returncode == 0:
                messagebox.showinfo("Success", f"Image '{image_name}' downloaded successfully.")
            else:
                messagebox.showerror("Error", f"Failed to download image: {result.stderr.strip()}")
        
        except FileNotFoundError:
            messagebox.showerror("Error", "Docker is not installed or not found in the system path.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def build_docker_image(self):
        """Build Docker image from a Dockerfile."""
        dockerfile_path = filedialog.askopenfilename(
            title="Select Dockerfile",
            filetypes=(("Dockerfile", "Dockerfile"), ("All Files", "*.*"))
        )
        if not dockerfile_path:
            messagebox.showerror("Error", "Please select a valid Dockerfile.")
            return

        image_name = simpledialog.askstring("Image Name", "Enter the name and tag for the image (e.g., myapp:latest):")
        if not image_name:
            messagebox.showerror("Error", "Please enter a valid image name and tag.")
            return

        try:
            result = subprocess.run(
                ["docker", "build", "-t", image_name, "-f", dockerfile_path, os.path.dirname(dockerfile_path)],
                capture_output=True, text=True, check=True
            )
            messagebox.showinfo("Success", f"Docker image built successfully:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to build Docker image:\n{e.stderr}")
    def stop_docker_container(self):
        """Stop a specific Docker container."""
        container_id = simpledialog.askstring("Container ID", "Enter the Container ID or Name to stop:")
        if not container_id:
            messagebox.showerror("Error", "Please enter a valid Container ID or Name.")
            return

        try:
            result = subprocess.run(["docker", "stop", container_id], capture_output=True, text=True, check=True)
            messagebox.showinfo("Success", f"Container stopped:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to stop container:\n{e.stderr}")

    def search_local_image(self):
        """Search for a Docker image locally."""
        image_name = simpledialog.askstring("Search Image", "Enter the image name/tag to search:")
        if not image_name:
            messagebox.showerror("Error", "Please enter a valid image name/tag.")
            return

        try:
            result = subprocess.run(["docker", "images", image_name], capture_output=True, text=True, check=True)
            if result.stdout.strip():
                messagebox.showinfo("Search Result", f"Image found:\n{result.stdout}")
            else:
                messagebox.showinfo("Search Result", "No matching image found locally.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error searching for image:\n{e.stderr}")

    def pull_docker_image(self):
        """Pull a Docker image from DockerHub."""
        image_name = simpledialog.askstring("Pull Image", "Enter the image name/tag to pull (e.g., ubuntu:latest):")
        if not image_name:
            messagebox.showerror("Error", "Please enter a valid image name/tag.")
            return

        try:
            result = subprocess.run(["docker", "pull", image_name], capture_output=True, text=True, check=True)
            messagebox.showinfo("Success", f"Image pulled successfully:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to pull image:\n{e.stderr}")


if __name__ == "__main__":
    app = DesktopApplication()
    app.mainloop()