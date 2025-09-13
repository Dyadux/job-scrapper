import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import csv
from datetime import datetime
import os
from naukri import NaukriLogin
from PIL import Image, ImageTk

class NaukriJobScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Naukri Job Scraper")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        style = ttk.Style()
        style.theme_use('clam')

        try:
            icon = Image.open("logo-2.png").resize((128, 128))
            self.icon_tk = ImageTk.PhotoImage(icon)
            self.root.iconphoto(True, self.icon_tk)
        except Exception as e:
            print(f"⚠️ Could not load icon: {e}")
        
        # Variables
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.job_title_var = tk.StringVar(value="Python Developer")
        self.location_var = tk.StringVar(value="Bangalore")
        self.experience_var = tk.StringVar(value="2")
        self.max_jobs_var = tk.StringVar(value="100")
        
        # Status variables
        self.is_running = False
        self.scraped_jobs = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Naukri Job Scraper", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Login Section
        login_frame = ttk.LabelFrame(main_frame, text="Login Credentials", padding="10")
        login_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        login_frame.columnconfigure(1, weight=1)
        
        ttk.Label(login_frame, text="Email:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        email_entry = ttk.Entry(login_frame, textvariable=self.email_var, width=40)
        email_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        password_entry = ttk.Entry(login_frame, textvariable=self.password_var, show="*", width=40)
        password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        
        # Search Parameters Section
        search_frame = ttk.LabelFrame(main_frame, text="Search Parameters", padding="10")
        search_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Job Title:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        job_title_entry = ttk.Entry(search_frame, textvariable=self.job_title_var, width=40)
        job_title_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Label(search_frame, text="Location:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        location_entry = ttk.Entry(search_frame, textvariable=self.location_var, width=40)
        location_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        
        ttk.Label(search_frame, text="Experience (Years):").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        experience_combo = ttk.Combobox(search_frame, textvariable=self.experience_var, 
                                      values=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], 
                                      state="readonly", width=37)
        experience_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        
        ttk.Label(search_frame, text="Max Jobs:").grid(row=3, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        max_jobs_entry = ttk.Entry(search_frame, textvariable=self.max_jobs_var, width=40)
        max_jobs_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
        
        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="Start Scraping", 
                                      command=self.start_scraping, style='Accent.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                     command=self.stop_scraping, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_button = ttk.Button(button_frame, text="Export to CSV", 
                                       command=self.export_to_csv, state='disabled')
        self.export_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="Clear Results", 
                                      command=self.clear_results)
        self.clear_button.pack(side=tk.LEFT)
        
        # Progress Section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Ready to start...")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Results Section
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Create Treeview for results
        columns = ('Job Title', 'Company', 'Experience', 'Location', 'Rating', 'Posted Date', 'Job ID')
        self.tree = ttk.Treeview(results_frame, columns=columns, show='headings', height=10)
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, minwidth=80)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid the treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
    def start_scraping(self):
        """Start the scraping process in a separate thread"""
        if not self.validate_inputs():
            return
            
        self.is_running = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.export_button.config(state='disabled')
        self.progress_bar.start()
        
        # Start scraping in a separate thread
        thread = threading.Thread(target=self.scrape_jobs)
        thread.daemon = True
        thread.start()
        
    def stop_scraping(self):
        """Stop the scraping process"""
        self.is_running = False
        self.update_progress("Stopping...")
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar.stop()
        
    def validate_inputs(self):
        """Validate user inputs"""
        if not self.email_var.get().strip():
            messagebox.showerror("Error", "Please enter your email")
            return False
        if not self.password_var.get().strip():
            messagebox.showerror("Error", "Please enter your password")
            return False
        if not self.job_title_var.get().strip():
            messagebox.showerror("Error", "Please enter a job title")
            return False
        if not self.location_var.get().strip():
            messagebox.showerror("Error", "Please enter a location")
            return False
        try:
            max_jobs = int(self.max_jobs_var.get())
            if max_jobs <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for max jobs")
            return False
        return True
        
    def scrape_jobs(self):
        """Main scraping function"""
        try:
            self.update_progress("Initializing browser...")
            self.update_status("Starting scraper...")
            
            # Initialize scraper
            scraper = NaukriLogin()
            
            if not self.is_running:
                return
                
            self.update_progress("Logging in to Naukri...")
            if not scraper.login(self.email_var.get(), self.password_var.get()):
                self.update_progress("Login failed!")
                self.update_status("Login failed - check credentials")
                messagebox.showerror("Error", "Login failed. Please check your credentials.")
                return
                
            if not self.is_running:
                return
                
            self.update_progress("Searching for jobs...")
            self.update_status("Searching jobs...")
            
            # Perform job search
            # if scraper.search_jobs(self.job_title_var.get()):
            #     self.update_progress("Extracting job details...")
            #     self.update_status("Extracting job details...")
                
            #     # Extract jobs with pagination
            #     jobs = scraper.extract_job_listings_with_pagination(
            #         max_jobs=int(self.max_jobs_var.get())
                    
            #     )
            #     if jobs:
            #         self.scraped_jobs = jobs
            #         self.populate_results(jobs)
            #         self.update_progress(f"Successfully scraped {len(jobs)} jobs!")
            #         self.update_status(f"Scraped {len(jobs)} jobs successfully")
            #         self.export_button.config(state='normal')
            #         messagebox.showinfo("Success", f"Successfully scraped {len(jobs)} jobs!")
            #     else:
            #         self.update_progress("No jobs found")
            #         self.update_status("No jobs found")
            #         messagebox.showwarning("Warning", "No jobs found for the given criteria")
            # else:
            #     self.update_progress("Job search failed")
            #     self.update_status("Job search failed")
            #     messagebox.showerror("Error", "Job search failed")

            self.update_progress("Extracting job details...")
            self.update_status("Extracting job details...")
            job_result = scraper.search_jobs(self.job_title_var.get(), self.location_var.get(), self.experience_var.get())
            
            if job_result[0]:
                
                
                # Extract jobs with pagination
                jobs = job_result[1]
                if jobs:
                    self.scraped_jobs = jobs
                    self.populate_results(jobs)
                    self.update_progress(f"Successfully scraped {len(jobs)} jobs!")
                    self.update_status(f"Scraped {len(jobs)} jobs successfully")
                    self.export_button.config(state='normal')
                    messagebox.showinfo("Success", f"Successfully scraped {len(jobs)} jobs!")
                else:
                    self.update_progress("No jobs found")
                    self.update_status("No jobs found")
                    messagebox.showwarning("Warning", "No jobs found for the given criteria")
            else:
                self.update_progress("Job search failed")
                self.update_status("Job search failed")
                messagebox.showerror("Error", "Job search failed")

                
        except Exception as e:
            self.update_progress(f"Error: {str(e)}")
            self.update_status(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.is_running = False
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.progress_bar.stop()
            
    def populate_results(self, jobs):
        """Populate the results treeview"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add jobs to treeview
        for job in jobs:
            self.tree.insert('', 'end', values=(
                job.get('title', 'N/A'),
                job.get('company', 'N/A'),
                job.get('experience', 'N/A'),
                job.get('location', 'N/A'),
                job.get('rating', 'N/A'),
                job.get('posted_date', 'N/A'),
                job.get('job_id', 'N/A')
            ))
            
    def export_to_csv(self):
        """Export scraped jobs to CSV file"""
        if not self.scraped_jobs:
            messagebox.showwarning("Warning", "No jobs to export")
            return
            
        # Ask user for file location
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"naukri_jobs_{timestamp}.csv"
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default_filename
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['Job Title', 'Company', 'Experience', 'Location', 'Rating', 
                                 'Posted Date', 'Skills', 'Description', 'Job Link', 'Job ID']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for job in self.scraped_jobs:
                        writer.writerow({
                            'Job Title': job.get('title', ''),
                            'Company': job.get('company', ''),
                            'Experience': job.get('experience', ''),
                            'Location': job.get('location', ''),
                            'Rating': job.get('rating', ''),
                            'Posted Date': job.get('posted_date', ''),
                            'Skills': ', '.join(job.get('skills', [])),
                            'Description': job.get('description', ''),
                            'Job Link': job.get('link', ''),
                            'Job ID': job.get('job_id', '')
                        })
                        
                messagebox.showinfo("Success", f"Jobs exported successfully to {filename}")
                self.update_status(f"Exported to {os.path.basename(filename)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")
                
    def clear_results(self):
        """Clear all results"""
        self.scraped_jobs = []
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.export_button.config(state='disabled')
        self.update_progress("Results cleared")
        self.update_status("Ready")
        
    def update_progress(self, message):
        """Update progress message"""
        self.progress_var.set(message)
        self.root.update_idletasks()
        
    def update_status(self, message):
        """Update status bar"""
        self.status_var.set(message)
        self.root.update_idletasks()

def main():
    root = tk.Tk()
    app = NaukriJobScraperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()