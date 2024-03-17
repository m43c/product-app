import tkinter as tk
from tkinter import ttk
import sqlite3


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Product Application")
        self.db_name = "database.db"

        # Create a style object
        style = ttk.Style()

        # Set font for all ttk widgets
        style.configure(".", font=("sans-serif", 10))

        # Creating a frame container
        frame = ttk.LabelFrame(
            self, text="Register a New Product", padding=(5, 5)
        )
        frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        # Name entry
        ttk.Label(frame, text="Name:").grid(
            row=0, column=0, padx=5, pady=2.5, sticky="w"
        )

        self.name = ttk.Entry(frame, font=("sans-serif", 10))
        self.name.focus()
        self.name.grid(row=0, column=1, padx=5, pady=2.5, ipady=1, sticky="w")

        # Price entry
        ttk.Label(frame, text="Price:").grid(
            row=1, column=0, padx=5, pady=2.5, sticky="w"
        )

        self.price = ttk.Entry(frame, font=("sans-serif", 10))
        self.price.grid(row=1, column=1, padx=5, pady=2.5, ipady=1, sticky="w")

        # Set a specific style for bold buttons
        style.configure("Bold.TButton", font=("sans-serif", 10, "bold"))

        # Button add Product
        ttk.Button(
            frame,
            text="Save Product",
            style="Bold.TButton",
            command=self.add_product,
        ).grid(row=2, columnspan=2, pady=5)

        # Outgoing message
        self.message = ttk.Label(self, text="", padding=(0, 10))

        # Table
        self.tree = ttk.Treeview(
            self,
            columns=("name", "price"),
            show="headings",
        )
        self.tree.grid(row=4, column=0, columnspan=3, padx=10)

        # Set a specific style for headers
        style.configure("Treeview.Heading", font=(None, 10, "bold"))

        # Define headings
        self.tree.heading("name", text="Name")
        self.tree.heading("price", text="Price")

        # Configurate column
        self.tree.column("name", anchor="center")
        self.tree.column("price", anchor="center")

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.tree.yview
        )
        scrollbar.grid(row=4, column=2, sticky="nse", padx=10)

        # Associate scrollbar with tree view
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Buttons to delete and edit products
        ttk.Button(
            self,
            text="Delete",
            style="Bold.TButton",
            command=self.delete_product,
        ).grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(
            self,
            text="Edit",
            style="Bold.TButton",
            command=self.edit_product,
        ).grid(row=5, column=1, columnspan=2, pady=10)

        # Show products in table
        self.get_products()

    def run_query(self, query, parameters=()):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                result = cursor.execute(query, parameters)
                conn.commit()

            return result
        except Exception as e:
            print(f"Error executing {e}")

    def get_products(self):
        try:
            # Clear the table before loading the data
            records = self.tree.get_children()

            for record in records:
                self.tree.delete(record)

            # Get products from database
            query = "SELECT * FROM product ORDER BY name ASC"
            products = self.run_query(query)

            # Show product records
            for product in products:
                self.tree.insert("", "end", values=(product[1], product[2]))
        except Exception as e:
            self.show_message("Error fetching products", "red")
            print(e)

    def show_message(self, message, color):
        self.message["text"] = message
        self.message.grid(row=3, column=0, columnspan=3)
        self.message.configure(foreground=color)
        self.after(3000, lambda: self.message.grid_forget())

    def input_validation(self):
        return len(self.name.get()) != 0 and len(self.price.get()) != 0

    def add_product(self):
        try:
            if self.input_validation():
                query = "INSERT INTO product (name, price) VALUES (?, ?)"
                parameters = (self.name.get(), self.price.get())

                self.run_query(query, parameters)

                # Show output message
                self.show_message(
                    f"{self.name.get()} product successfully added", "green"
                )

                # Clear name and price entry
                self.name.delete(0, "end")
                self.price.delete(0, "end")
            else:
                self.show_message(f"Name and price is required", "red")

            # Update products
            self.get_products()
        except Exception as e:
            self.show_message("Error adding product", "red")
            print(e)

    def delete_product(self):
        try:
            selected_item = self.tree.item(self.tree.selection())["values"]

            if selected_item:
                product_name = selected_item[0]

                # Create and run query
                query = "DELETE FROM product WHERE name = ?"
                parameters = (product_name,)

                self.run_query(query, parameters)

                # Update products
                self.get_products()
            else:
                self.show_message("Please select a product", "red")
        except Exception as e:
            self.show_message("Error deleting product", "red")
            print(e)

    def edit_product(self):
        selected_item = self.tree.item(self.tree.selection())["values"]

        if selected_item:
            current_name = tk.StringVar(value=selected_item[0])
            current_price = tk.StringVar(value=selected_item[1])

            ProductEdition(self, current_name, current_price)
        else:
            self.show_message("Please select a product", "red")


class ProductEdition(tk.Toplevel):
    def __init__(self, main_wind, current_name, current_price):
        self.main_wind = main_wind
        self.current_name = current_name
        self.current_price = current_price

        super().__init__()

        self.title("Product Edition")
        self.configure(padx=10, pady=5)

        # Current product name
        ttk.Label(self, text="Current Name:").grid(
            row=0, column=0, padx=5, pady=2.5, sticky="w"
        )

        self.product_name_entry = ttk.Entry(
            self,
            textvariable=self.current_name,
            font=("sans-serif", 10),
            state="readonly",
        )
        self.product_name_entry.grid(
            row=0, column=1, padx=5, pady=2.5, ipady=1, sticky="w"
        )

        # New product name
        ttk.Label(self, text="New Name:").grid(
            row=1, column=0, padx=5, pady=2.5, sticky="w"
        )

        self.entry_new_name = ttk.Entry(self, font=("sans-serif", 10))
        self.entry_new_name.grid(
            row=1, column=1, padx=5, pady=2.5, ipady=1, sticky="w"
        )

        # Current product price
        ttk.Label(self, text="Current Price:").grid(
            row=2, column=0, padx=5, pady=2.5, sticky="w"
        )
        ttk.Entry(
            self,
            textvariable=self.current_price,
            font=("sans-serif", 10),
            state="readonly",
        ).grid(row=2, column=1, padx=5, pady=2.5, ipady=1, sticky="w")

        # New product price
        ttk.Label(self, text="New Price:").grid(
            row=3, column=0, padx=5, pady=2.5, sticky="w"
        )

        self.entry_new_price = ttk.Entry(self, font=("sans-serif", 10))
        self.entry_new_price.grid(
            row=3, column=1, padx=5, pady=2.5, ipady=1, sticky="w"
        )

        # Button to save new product information
        ttk.Button(
            self,
            text="Save New Product",
            style="Bold.TButton",
            command=self.update_product,
        ).grid(row=4, columnspan=2, pady=10)

    def update_product(self):
        try:
            new_name = self.entry_new_name.get()
            new_price = float(self.entry_new_price.get())

            query = """
            UPDATE product
            SET name = ?,
                price = ?
            WHERE name = ? AND price = ?
            """
            parameters = (
                new_name,
                new_price,
                self.current_name.get(),
                float(self.current_price.get()),
            )

            result = app.run_query(query, parameters)

            if result:
                self.main_wind.show_message(
                    "Product successfully updated", "green"
                )
            else:
                self.main_wind.show_message("Error updating product", "red")

            self.main_wind.get_products()
            self.destroy()
        except ValueError:
            self.main_wind.show_message("Invalid price format", "red")
        except Exception as e:
            self.main_wind.show_message(f"Error updating product", "red")
            print(e)


if __name__ == "__main__":
    app = App()
    app.mainloop()
