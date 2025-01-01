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


        self.homepage()

    def add_return_button(self, frame):
        """Add a button to return to the homepage"""
        return_btn = ctk.CTkButton(
            frame, 
            text="Return to Homepage", 
            command=lambda: self.return_to_homepage(frame),
            bg_color='#135E4B',
            fg_color='#135E4B',
            hover_color='#A1D8B5',
            corner_radius=30
        )
        return_btn.grid(row=5, column=0, padx=10, pady=10)

    def return_to_homepage(self, frame):
        """Return to the homepage"""
        if frame:
            frame.pack_forget()  # Hide current frame
            self.homepage()  # Recreate and show homepage

        
    def homepage(self):
        """Display the homepage with Application Features"""
        # Create homepage frame
        self.homepage_frame = ctk.CTkFrame(self, bg_color=self.GREEN_LIGHT, fg_color=self.GREEN_LIGHT)
        self.homepage_frame.pack(expand=True, fill=BOTH, padx=20, pady=20)
        
        self.hompage_label = ctk.CTkLabel(self.homepage_frame, text="Cloud Management System", 
                                          font=('Helvetica', 20, 'bold'))
        self.hompage_label.pack(pady=10)
        
        # Create buttons for different sections
        sections = [
            ("Virtual Machines", self.show_vm_section),
            ("Docker Files", self.show_docker_files_section),
            ("Docker Hub", self.display_docker_hub_section),
            ("Manage Containers", self.show_containers_section),
            ("Docker Control Panel", self.docker_control_panel)
        ]

        for text, command in sections:
            btn = ctk.CTkButton(self.homepage_frame, 
                                text=text, 
                                command=command,
                                width=400,
                                height=50)
            btn.pack(pady=10)

    def show_vm_section(self):
        """Display Virtual Machine configuration section"""
        # Hide the homepage
        if self.homepage_frame:
            self.homepage_frame.pack_forget()

        # VM Configuration Frame
        self.vm_frame = ctk.CTkFrame(self, bg_color='#4CB572', fg_color='#4CB572')
        self.vm_frame.pack(expand=True, fill=ctk.BOTH, padx=20, pady=20)
        # Title
        title_label = ctk.CTkLabel(self.vm_frame, text="Virtual Machine Configuration", 
                                   font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, padx=10, pady=10)

        # Configuration Inputs
        config_frame = ctk.CTkFrame(self.vm_frame, bg_color='#4CB572', fg_color='#4CB572')
        config_frame.grid(row=1, column=0, padx=10, pady=10)

        # CPU Configuration
        cpu_label = ctk.CTkLabel(config_frame, text="Number of CPUs:", font=('Helvetica', 16, 'bold'))
        cpu_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        cpu_entry = ctk.CTkEntry(config_frame, textvariable=self.cpu_var, width=120)
        cpu_entry.grid(row=0, column=2, padx=5, pady=5, sticky='w')

        # Memory Configuration
        memory_label = ctk.CTkLabel(config_frame, text="Memory (MB):", font=('Helvetica', 16, 'bold'))
        memory_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')
        memory_entry = ctk.CTkEntry(config_frame, textvariable=self.memory_var, width=120)
        memory_entry.grid(row=1, column=2, padx=5, pady=5, sticky='w')

        # Disk Image Configuration
        disk_label = ctk.CTkLabel(config_frame, text="Disk Image Path:", font=('Helvetica', 16, 'bold'))
        disk_label.grid(row=2, column=0, padx=5, pady=5, sticky='e')
        disk_entry = ctk.CTkEntry(config_frame, textvariable=self.disk_var, width=120)
        disk_entry.grid(row=2, column=2, padx=5, pady=5, sticky='w')
        
        # Browse Disk Button
        browse_btn = ctk.CTkButton(config_frame, text="Browse", command=self.browse_disk,
                                   bg_color='#135E4B', fg_color='#135E4B', hover_color='#A1D8B5',
                                   corner_radius=30, width=70)
        browse_btn.grid(row=4, column=2, padx=5, pady=5)

        # Create VM Button
        create_vm_btn = ctk.CTkButton(self.vm_frame, text="Create Virtual Machine", 
                                      command=self.create_vm, bg_color='#135E4B', 
                                      fg_color='#135E4B', hover_color='#A1D8B5',
                                      corner_radius=30)
        create_vm_btn.grid(row=2, column=0, padx=10, pady=10)
        # List VMs Button
        list_vms_btn = ctk.CTkButton(self.vm_frame, text="List Virtual Machines", 
                                    command=self.list_vms, bg_color='#135E4B', 
                                    fg_color='#135E4B', hover_color='#A1D8B5',
                                    corner_radius=30)
        list_vms_btn.grid(row=3, column=0, padx=10, pady=10)
        vm_listbox=ctk.CTkTextbox(self.vm_frame, width=300, height=200)
        vm_listbox.grid(row=4, column=0, padx=10, pady=10)
        
                
        # Add return button
        self.add_return_button(self.vm_frame)
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
        self.vm_listbox.delete("1.0", "end") 
        try:
            # Run the command to list VMs
            result = subprocess.run(
                ["virsh", "list", "--all"],
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.strip().split('\n')[2:]  # Skip the header lines

            # Parse each line of output
            for line in lines:
                if line.strip():  # Ignore empty lines
                    parts = line.split(maxsplit=2)  # Split into up to 3 parts (ID, Name, State)
                    if len(parts) == 3:
                        vm_id, vm_name, vm_state = parts
                        self.vm_listbox.insert(ctk.END, f"ID: {vm_id}, Name: {vm_name}, State: {vm_state}")
                    else:
                        self.vm_listbox.insert(ctk.END, f"Unrecognized format: {line}")

        except subprocess.CalledProcessError as e:
            messagebox.showwarning("Warning", f"Unable to list VMs. Error: {e}")
        except FileNotFoundError:
            messagebox.showerror("Error", "Virtualization management tool not found. Please install it.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            
            
                
    def show_docker_files_section(self):
            """Display Docker Files section"""
            #Remove homepage frame
            if self.homepage_frame:
                self.homepage_frame.destroy()
                
            # Docker Files Frame
            self.docker_frame = ctk.CTkFrame(self, bg_color='#4CB572', fg_color='#4CB572')
            self.docker_frame.pack(expand=True, fill=ctk.BOTH, padx=20, pady=20)

            # Title
            title_label = ctk.CTkLabel(self.docker_frame, text="Docker Files Management",
                                    font=('Helvetica', 16, 'bold'))
            title_label.grid(row=0, column=0, padx=10, pady=10)

            # Dockerfile Creation Section
            create_frame = ctk.CTkFrame(self.docker_frame, bg_color='#4CB572', fg_color='#4CB572')
            create_frame.grid(row=1, column=0, padx=10, pady=10)

            # Base Image Input
            base_image_label = ctk.CTkLabel(create_frame, text="Base Image:")
            base_image_label.grid(row=0, column=0, padx=5, pady=5, sticky='w')
            self.base_image_entry = ctk.CTkEntry(create_frame, width=300)
            self.base_image_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')

            # Commands Input
            commands_label = ctk.CTkLabel(create_frame, text="Commands (one per line):")
            commands_label.grid(row=1, column=0, padx=5, pady=5, sticky='w')
            self.commands_text = ctk.CTkTextbox(create_frame, height=100, width=300)
            self.commands_text.grid(row=1, column=1, padx=5, pady=5, sticky='w')

            # Environment Variables Input
            env_vars_label = ctk.CTkLabel(create_frame, text="Environment Variables (KEY=VALUE, one per line):")
            env_vars_label.grid(row=2, column=0, padx=5, pady=5, sticky='w')
            self.env_vars_text = ctk.CTkTextbox(create_frame, height=60, width=300)
            self.env_vars_text.grid(row=2, column=1, padx=5, pady=5, sticky='w')

            # Ports Input
            ports_label = ctk.CTkLabel(create_frame, text="Exposed Ports (comma-separated):")
            ports_label.grid(row=3, column=0, padx=5, pady=5, sticky='w')
            self.ports_entry = ctk.CTkEntry(create_frame, width=300)
            self.ports_entry.grid(row=3, column=1, padx=5, pady=5, sticky='w')
            
            # Dockerfile Path
            path_label = ctk.CTkLabel(create_frame, text="Dockerfile Path:")
            path_label.grid(row=4, column=0, padx=5, pady=5, sticky='w')
            self.path_entry = ctk.CTkEntry(create_frame, textvariable=self.dockerfile_path_var, width=300)
            self.path_entry.grid(row=4, column=1, padx=5, pady=5, sticky='w')
            browse_btn = ctk.CTkButton(create_frame, text="Browse", command=self.set_dockerfile_path,
                                    bg_color='#135E4B', fg_color='#135E4B', hover_color='#A1D8B5',
                                    corner_radius=30, width=70)
            browse_btn.grid(row=4, column=2, padx=5, pady=5, sticky='w')

            # Create Dockerfile Button
            create_btn = ctk.CTkButton(self.docker_frame, text="Create Dockerfile", command=self.create_dockerfile,
                                        bg_color='#135E4B', fg_color='#135E4B', hover_color='#A1D8B5',
                                        corner_radius=30, width=120)
            create_btn.grid(row=2, column=0, padx=10, pady=10)
            # Add return button
            self.add_return_button(self.docker_frame)
            
    def set_dockerfile_path(self):
        """Set path for Dockerfile"""
        path = ctk.filedialog.askdirectory(title="Select Dockerfile Save Location")
        if path:
            self.dockerfile_path_var.set(os.path.join(path, "Dockerfile"))

    def create_dockerfile(self):
        """Create a new Dockerfile"""
        save_path = self.dockerfile_path_var.get()
        if not save_path:
            ctk.messagebox.showerror("Error", "Please specify a path to save the Dockerfile.")
            return

        # Gather inputs
        base_image = self.base_image_entry.get().strip()
        commands = self.commands_text.get("1.0", "end").strip()
        env_vars = self.env_vars_text.get("1.0", "end").strip()
        ports = self.ports_entry.get().strip()

        # Generate Dockerfile content
        dockerfile_content = f"FROM {base_image or 'ubuntu:latest'}\n"

        if env_vars:
            for env in env_vars.splitlines():
                dockerfile_content += f"ENV {env.strip()}\n"

        if commands:
            for cmd in commands.splitlines():
                dockerfile_content += f"RUN {cmd.strip()}\n"

        if ports:
            for port in ports.split(','):
                dockerfile_content += f"EXPOSE {port.strip()}\n"

        try:
            with open(save_path, "w") as f:
                f.write(dockerfile_content)
            ctk.messagebox.showinfo("Success", f"Dockerfile created at {save_path}")
        except Exception as e:
            ctk.messagebox.showerror("Error", f"Failed to create Dockerfile: {str(e)}")



    def display_docker_hub_section(self):
        """Display Docker Hub section"""
        # Clear previous content
        if self.homepage_frame:
            self.homepage_frame.pack_forget()

        # Docker Hub Frame
        hub_frame = ctk.CTkFrame(self, bg_color='#4CB572', fg_color='#4CB572')
        hub_frame.pack(expand=True, fill=ctk.BOTH, padx=20, pady=20)

        # Search Frame
        search_frame = ctk.CTkFrame(hub_frame, bg_color='#4CB572', fg_color='#4CB572')
        search_frame.grid(row=0, column=0, padx=10, pady=10)

        # Search Entry
        search_label = ctk.CTkLabel(search_frame, text="Search Docker Hub:")
        search_label.grid(row=0, column=0, padx=5, pady=5)
        search_entry = ctk.CTkEntry(search_frame, width=300)
        search_entry.grid(row=0, column=1, padx=5, pady=5)

        # Search Button
        search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            command=lambda: self.search_docker_hub(search_entry.get()),
            bg_color='#135E4B',
            fg_color='#135E4B',
            hover_color='#A1D8B5',
            corner_radius=30,
            width=70
        )
        search_btn.grid(row=0, column=2, padx=5, pady=5)
        

        # Results Textbox
        self.docker_hub_listbox = ctk.CTkTextbox(hub_frame, width=300, height=200)
        self.docker_hub_listbox.grid(row=1, column=0, padx=10, pady=10)
        # Add return button
        self.add_return_button(hub_frame)

    def search_docker_hub(self, query):
        """Search Docker Hub for images"""
        self.docker_hub_listbox.delete("1.0", "end")  # Clear previous results
        try:
            # Query the Docker Hub API
            response = requests.get(f"https://hub.docker.com/v2/search/repositories/?query={query}")
            response.raise_for_status()
            results = response.json().get('results', [])
            
            if not results:
                self.docker_hub_listbox.insert("end", "No results found.\n")
                return

            # Insert container names into the textbox
            for result in results:
                container_name = result.get('name', 'N/A')  # Adjust the key if necessary
                repo_name = result.get('repo_name', 'N/A')
                stars = result.get('star_count', 0)
                self.docker_hub_listbox.insert("end", f"Container: {container_name} | Repository: {repo_name} | Stars: {stars}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search Docker Hub: {str(e)}")
    def show_containers_section(self):
        """Display Containers Management section"""
            #Remove homepage frame
        if self.homepage_frame:
            self.homepage_frame.destroy()

        # Containers Frame
        self.containers_frame = ctk.CTkFrame(self, bg_color='#4CB572', fg_color='#4CB572')
        self.containers_frame.pack(expand=True, fill=ctk.BOTH, padx=20, pady=20)

        # Buttons Frame
        btn_frame = ctk.CTkFrame(self.containers_frame,  bg_color='#4CB572', fg_color='#4CB572')
        btn_frame.grid(row=0, column=0, padx=10, pady=10)

        # List Images Button
        list_images_btn = ctk.CTkButton(btn_frame, text="List Docker Images", 
                                        command=self.list_docker_images,
                                        bg_color='#135E4B', fg_color='#135E4B', hover_color='#A1D8B5',
                                        background_corner_colors=(['#135E4B', '#135E4B', '#135E4B', '#135E4B']),
                                        corner_radius=30, width=70)
        list_images_btn.grid(row=0, column=0, padx=5)

        # List Containers Button
        list_containers_btn = ctk.CTkButton(btn_frame, text="List Docker Containers", 
                                            command=self.list_docker_containers,
                                            bg_color='#135E4B', fg_color='#135E4B', hover_color='#A1D8B5',
                                            background_corner_colors=(['#135E4B', '#135E4B', '#135E4B', '#135E4B']),
                                            corner_radius=30, width=70)
        list_containers_btn.grid(row=0, column=1, padx=5)

        # Listboxes Frame
        list_frame = ctk.CTkFrame(self.containers_frame)
        list_frame.grid(row=1, column=0, padx=10, pady=10)

        # Images Label and Listbox
        images_label = ctk.CTkLabel(list_frame, text="Docker Images:")
        images_label.grid(row=0, column=0, padx=5, pady=5)
        self.images_listbox = ctk.CTkTextbox(list_frame, width=70, height=10)
        self.images_listbox.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # Containers Label and Listbox
        containers_label = ctk.CTkLabel(list_frame, text="Docker Containers:")
        containers_label.grid(row=2, column=0, padx=5, pady=5)
        self.containers_listbox = ctk.CTkTextbox(list_frame, width=70, height=10)
        self.containers_listbox.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")
        
        # Make the list_frame grid expand properly
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_rowconfigure(3, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        # Add return button
        self.add_return_button(self.containers_frame)

    def list_docker_images(self):
        """List all Docker images on the system"""
        self.images_listbox.delete("1.0", "end")  # Clear the listbox
        try:
            # Run `docker images` command
            result = subprocess.run(["docker", "images"], capture_output=True, text=True, check=True)
            output = result.stdout.strip().split('\n')

            # Skip the header and add images
            if len(output) > 1:
                for line in output[1:]:  # Skip header
                    columns = line.split()  # Adjust as necessary for your output format
                    if columns:
                        self.images_listbox.insert("end", f"{columns[0]}:{columns[1]}\n")
            else:
                self.images_listbox.insert("end", "No Docker images found.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to list Docker images: {str(e)}")
        except FileNotFoundError:
            messagebox.showerror("Error", "Docker is not installed or not in PATH.")
            
    def list_docker_containers(self):
        """List Docker containers in the listbox."""
        self.containers_listbox.delete("1.0", "end")  # Clear the listbox
        try:
            # Run the `docker ps -a` command
            result = subprocess.run(["docker", "ps", "-a"], capture_output=True, text=True, check=True)
            containers = result.stdout.strip().split('\n')
            
            if len(containers) > 1:  # If there are containers
                header = containers[0]  # Header row
                self.containers_listbox.insert("end", f"{header}\n{'-' * len(header)}\n") 
                
                for container in containers[1:]:  # Skip the header
                    self.containers_listbox.insert("end", f"{container}\n")
            else:
                self.containers_listbox.insert("end", "No containers found.\n")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to list containers: {str(e)}")
        except FileNotFoundError:
            messagebox.showerror("Error", "Docker is not installed or not in PATH.")


    def docker_control_panel(self):
            """Set up the Docker control panel layout"""
            if self.homepage_frame:
                self.homepage_frame.destroy()

            # Docker control frame for containers
            self.docker_control_frame = ctk.CTkFrame(self,bg_color='#4CB572', fg_color='#4CB572')
            self.docker_control_frame.pack(expand=True, fill=ctk.BOTH, padx=20, pady=20)

            # Feature 1: Stop container
            self.stop_container_label = ctk.CTkLabel(self.docker_control_frame, text="Container ID/Name:")
            self.stop_container_label.grid(row=0, column=0, padx=10, pady=5)

            self.stop_container_entry = ctk.CTkEntry(self.docker_control_frame, width=150)
            self.stop_container_entry.grid(row=0, column=1, padx=10, pady=5)

            self.stop_button = ctk.CTkButton(self.docker_control_frame, text="Stop Selected Container", command=self.stop_selected_container)
            self.stop_button.grid(row=0, column=2, padx=10, pady=5)

            # Feature 2: Download Docker Image
            self.download_button = ctk.CTkButton(self.docker_control_frame, text="Download Image", command=self.download_image)
            self.download_button.grid(row=1, column=0, padx=10, pady=5)

            # Feature 4: Build Docker Image
            self.build_image_label = ctk.CTkLabel(self.docker_control_frame, text="Dockerfile Path:")
            self.build_image_label.grid(row=2, column=0, padx=10, pady=5)

            self.build_image_entry = ctk.CTkEntry(self.docker_control_frame, width=150)
            self.build_image_entry.grid(row=2, column=1, padx=10, pady=5)

            self.build_button = ctk.CTkButton(self.docker_control_frame, text="Browse Dockerfike", command=self.browse_disk_dockerfile)
            self.build_button.grid(row=2, column=2, padx=10, pady=5)
            
            self.build_image_name_label = ctk.CTkLabel(self.docker_control_frame, text="Enter Docker image name:")
            self.build_image_name_label.grid(row=3, column=0, padx=10, pady=5)
            
            self.build_image_name_entry = ctk.CTkEntry(self.docker_control_frame, width=150)
            self.build_image_name_entry.grid(row=3, column=1, padx=10, pady=5)

            self.build_button = ctk.CTkButton(self.docker_control_frame, text="Build Image", command=self.build_docker_image)
            self.build_button.grid(row=3, column=2, padx=10, pady=5)    

            # Feature 5: Pull Docker Image
            self.pull_image_label = ctk.CTkLabel(self.docker_control_frame, text="Pull Image Name:")
            self.pull_image_label.grid(row=4, column=0, padx=10, pady=5)

            self.pull_image_entry = ctk.CTkEntry(self.docker_control_frame, width=150)
            self.pull_image_entry.grid(row=4, column=1, padx=10, pady=5)

            self.pull_button = ctk.CTkButton(self.docker_control_frame, text="Pull Image", command=self.pull_docker_image)
            self.pull_button.grid(row=4, column=2, padx=10, pady=5)

            # Feature 6: Search Local Image
            self.local_search_label = ctk.CTkLabel(self.docker_control_frame, text="Search Local Image:")
            self.local_search_label.grid(row=5, column=0, padx=10, pady=5)

            self.local_search_entry = ctk.CTkEntry(self.docker_control_frame, width=150)
            self.local_search_entry.grid(row=5, column=1, padx=10, pady=5)

            self.local_search_button = ctk.CTkButton(self.docker_control_frame, text="Search Local Image", command=self.search_local_image)
            self.local_search_button.grid(row=5, column=2, padx=10, pady=5)
            # Add return button
            self.add_return_button(self.docker_control_frame)

    
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
        dockerfile_path = self.build_image_entry.get().strip()
        if not dockerfile_path:
            messagebox.showerror("Error", "Please select a valid Dockerfile.")
            return

        image_name = self.build_image_name_entry.get().strip()
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
        container_id = self.stop_container_entry.get().strip()
        if not container_id:
            messagebox.showerror("Error", "Please enter a valid Container ID or Name.")
            return

        try:
            result = subprocess.run(["docker", "stop", container_id], capture_output=True, text=True, check=True)
            messagebox.showinfo("Success", f"Container stopped:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to stop container:\n{e.stderr}")
            
    def browse_disk_dockerfile(self):
        """Browse for a Dockerfile path."""
        file_path = filedialog.askopenfilename(
            title="Select Dockerfile",
            filetypes=(("Dockerfiles", "Dockerfile"), ("All Files", "*.*"))
        )
        if file_path:
            self.build_image_entry.delete(0, "end")  # Clear any existing text
            self.build_image_entry.insert(0, file_path)  # Insert selected path


    def search_local_image(self):
        """Search for a Docker image locally."""
        image_name = self.local_search_entry.get().strip()
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
        image_name =self.pull_image_entry.get().strip()
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