    def apply_filters(self):
        if self.cleaned_data is None:
            messagebox.showwarning("Data Not Available", "Please clean and merge data first.")
            return
        
        try:
            min_year = int(self.year_entry.get())
            min_height = float(self.height_entry.get())
            filtered_data = self.cleaned_data[
                (self.cleaned_data['Year'] >= min_year) & 
                (self.cleaned_data['Site Height'] > min_height)
            ]
            printStats(filtered_data)
            messagebox.showinfo("Filtered Stats Displayed", "Filtered power statistics displayed in console.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for year and site height.")

                    # Range Manipulation
        tk.Label(root, text="Enter Minimum Year (for range)").pack(pady=5)
        self.year_entry = tk.Entry(root)
        self.year_entry.pack()
        tk.Label(root, text="Enter Minimum Site Height (for range)").pack(pady=5)
        self.height_entry = tk.Entry(root)
        self.height_entry.pack()
        tk.Button(root, text="Apply Filters and Display Power Statistics", command=self.apply_filters).pack(pady=5)