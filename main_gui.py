import tkinter as tk
from tkinter import messagebox, filedialog
import json
import pandas as pd

from data_processing import clean_data
from statistics_handler import printStats
from visualization import visualize_multiplex_data
from correlation_analysis import analyze_correlation

class DABDataGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DAB Data Interface")
        self.file_path = {"Antenna": "", "Params": ""}
        self.cleaned_data = None
        
        # Load, Clean, and Save Dataset
        tk.Button(root, text="Load Antenna CSV", command=self.load_antenna).pack(pady=5)
        tk.Button(root, text="Load Params CSV", command=self.load_params).pack(pady=5)
        tk.Button(root, text="Clean and Merge Data", command=self.clean_and_merge_data).pack(pady=5)
        tk.Button(root, text="Save Cleaned Data", command=self.save_cleaned_data).pack(pady=5)
        tk.Button(root, text="Load Prepared Data", command=self.load_prepared_data).pack(pady=5)
        # Display Stats
        tk.Button(root, text="Display Power Statistics", command=self.display_stats).pack(pady=10)
        
        # Visualization and Analysis
        tk.Button(root, text="Visualize Multiplex Data", command=visualize_multiplex_data).pack(pady=5)
        tk.Button(root, text="Analyze Correlations", command=self.analyze_correlations).pack(pady=5)

    def load_antenna(self):
        self.file_path["Antenna"] = filedialog.askopenfilename(title="Select Antenna CSV File",
                                                                filetypes=[("CSV file", "*.csv")])
        messagebox.showinfo("File Loaded", f"Antenna CSV loaded: {self.file_path['Antenna']}")

    def load_params(self):
        self.file_path["Params"] = filedialog.askopenfilename(title="Select Params CSV File", 
                                                              filetypes=[("CSV file", "*.csv")])
        messagebox.showinfo("File Loaded", f"Params CSV loaded: {self.file_path['Params']}")

    def clean_and_merge_data(self):
        if not self.file_path["Antenna"] or not self.file_path["Params"]:
            messagebox.showwarning("Missing Files", "Please load both Antenna and Params CSV files.")
            return
        self.cleaned_data = clean_data(self.file_path)
        messagebox.showinfo("Data Cleaned", "Data has been cleaned and merged successfully.")

    def load_prepared_data(self):
        file_path = filedialog.askopenfilename(
            title="Select Prepared Data JSON File",
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:  # Proceed only if a file is selected
            try:
                # Load the JSON file into a DataFrame
                with open(file_path, "r") as file:
                    data = json.load(file)
                self.cleaned_data = pd.DataFrame(data)
                messagebox.showinfo("Data Load", f"Prepared data successfully loaded from: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        else:
            messagebox.showwarning("File Selection", "No file selected.")
            
    def save_cleaned_data(self):
        if self.cleaned_data is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if save_path:
                self.cleaned_data.to_json(save_path, orient='records', indent=4)
                messagebox.showinfo("Data Saved", f"Data saved to: {save_path}")
        else:
            messagebox.showwarning("Data Not Cleaned", "Please clean and merge data first.")

    def display_stats(self):
        if self.cleaned_data is not None:
            printStats(self.cleaned_data)
            messagebox.showinfo("Stats Displayed", "Power statistics have been displayed in the console.")
        else:
            messagebox.showwarning("Data Not Available", "Please clean and merge data first.")

    def analyze_correlations(self):
        if self.cleaned_data is not None:
            analyze_correlation(self.cleaned_data)
        else:
            messagebox.showwarning("Data Not Available", "Please clean and merge data first.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DABDataGUI(root)
    root.mainloop()