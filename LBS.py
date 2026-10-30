import tkinter as tk
from tkinter import messagebox
import csv
import os

FILENAME = "library.csv"

# ---------- Data helpers ----------

def read_books():
    """Read all valid rows from CSV. Skips malformed/blank rows."""
    books = []
    if not os.path.exists(FILENAME):
        return books
    try:
        with open(FILENAME, "r", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row or len(row) < 4:
                    continue
                row = [col.strip() for col in row]
                if not row[3].isdigit():
                    continue
                books.append(row)
    except OSError as e:
        messagebox.showerror("File Error", f"Could not read library file:\n{e}")
    return books


def write_books(books):
    """Overwrite the CSV with the given list of rows."""
    try:
        with open(FILENAME, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(books)
    except OSError as e:
        messagebox.showerror("File Error", f"Could not save library file:\n{e}")


# ---------- Actions ----------

def add_book():
    bid = book_id.get().strip()
    title = book_title.get().strip()
    author = book_author.get().strip()
    qty = book_qty.get().strip()

    if not bid:
        messagebox.showerror("Error", "Please enter a Book ID.")
        return

    # Quantity is optional for existing books (defaults to 1 copy)
    if qty and (not qty.isdigit() or int(qty) <= 0):
        messagebox.showerror("Error", "Quantity must be a positive number.")
        return

    books = read_books()

    # Case 1: Book ID already exists -> just add copies
    for row in books:
        if row[0] == bid:
            # If a title was typed, make sure it matches the existing book
            if title and title.lower() != row[1].lower():
                messagebox.showerror(
                    "Error",
                    f"Book ID '{bid}' belongs to '{row[1]}'. "
                    "Clear the Title field or use a different ID."
                )
                return
            copies = int(qty) if qty else 1
            row[3] = str(int(row[3]) + copies)
            write_books(books)
            messagebox.showinfo("Success", f"Book already exists. Added {copies} copy/copies.")
            clear_entries()
            display_books()
            return

    # Case 2: New book -> all details required
    if not (title and author and qty):
        messagebox.showerror(
            "Error",
            "This is a new Book ID. Please enter Title, Author and Quantity."
        )
        return

    books.append([bid, title, author, qty])
    write_books(books)
    messagebox.showinfo("Success", "New book added successfully!")
    clear_entries()
    display_books()


def display_books():
    text_box.delete("1.0", tk.END)
    books = read_books()
    if not books:
        text_box.insert(tk.END, "No books available.\n")
        return

    header = f"{'ID':<10}{'Title':<25}{'Author':<20}{'Qty':<5}\n"
    text_box.insert(tk.END, header)
    text_box.insert(tk.END, "-" * 60 + "\n")
    for row in books:
        line = f"{row[0]:<10}{row[1]:<25}{row[2]:<20}{row[3]:<5}\n"
        text_box.insert(tk.END, line)


def search_book():
    key = search_entry.get().strip().lower()
    if not key:
        messagebox.showinfo("Info", "Enter a Book ID, title or author to search.")
        return

    # Match against ID, title and author (partial, case-insensitive)
    results = [
        row for row in read_books()
        if key in row[0].lower() or key in row[1].lower() or key in row[2].lower()
    ]

    text_box.delete("1.0", tk.END)
    if not results:
        text_box.insert(tk.END, "Book not found.\n")
        return

    header = f"{'ID':<10}{'Title':<25}{'Author':<20}{'Qty':<5}\n"
    text_box.insert(tk.END, header)
    text_box.insert(tk.END, "-" * 60 + "\n")
    for row in results:
        text_box.insert(tk.END, f"{row[0]:<10}{row[1]:<25}{row[2]:<20}{row[3]:<5}\n")


def restock_book():
    """Add additional copies to an existing Book ID (uses the Quantity field as the amount to add)."""
    bid = book_id.get().strip()
    amount = book_qty.get().strip()

    if not bid:
        messagebox.showerror("Error", "Enter the Book ID to restock in the Book ID box (left).")
        return
    if not amount.isdigit() or int(amount) <= 0:
        messagebox.showerror("Error", "Enter a positive number in the Quantity box for how many copies to add.")
        return

    books = read_books()
    updated = False
    for row in books:
        if row[0] == bid:
            row[3] = str(int(row[3]) + int(amount))
            updated = True
            break

    if not updated:
        messagebox.showerror("Error", "Book ID not found. Use 'Add Book' first to create a new entry.")
        return

    write_books(books)
    messagebox.showinfo("Success", f"Added {amount} copies. Book restocked successfully!")
    clear_entries()
    display_books()


def issue_book():
    update_quantity(-1, "issued")


def return_book():
    update_quantity(1, "returned")


def update_quantity(change, action):
    bid = book_id.get().strip()
    amount_text = book_qty.get().strip()

    if not bid:
        messagebox.showerror("Error", "Enter Book ID in the Book ID box (left).")
        return

    # Quantity box = how many copies to issue/return (defaults to 1 if empty)
    if amount_text:
        if not amount_text.isdigit() or int(amount_text) <= 0:
            messagebox.showerror("Error", "Quantity must be a positive number.")
            return
        amount = int(amount_text)
    else:
        amount = 1

    books = read_books()
    updated = False
    for row in books:
        if row[0] == bid:
            qty = int(row[3]) + change * amount
            if qty < 0:
                messagebox.showerror(
                    "Error",
                    f"Only {row[3]} copy/copies available. Cannot issue {amount}."
                )
                return
            row[3] = str(qty)
            updated = True
            break

    if not updated:
        messagebox.showerror("Error", "Book ID not found.")
        return

    write_books(books)
    messagebox.showinfo("Success", f"{amount} book(s) {action} successfully!")
    clear_entries()
    display_books()


def delete_book():
    bid = book_id.get().strip()
    if not bid:
        messagebox.showerror("Error", "Enter Book ID to delete in the Book ID box (left).")
        return
    books = read_books()
    new_books = [r for r in books if r[0] != bid]
    if len(new_books) == len(books):
        messagebox.showerror("Error", "Book ID not found.")
        return
    write_books(new_books)
    messagebox.showinfo("Success", "Book deleted successfully.")
    display_books()


def clear_entries():
    book_id.delete(0, tk.END)
    book_title.delete(0, tk.END)
    book_author.delete(0, tk.END)
    book_qty.delete(0, tk.END)
    search_entry.delete(0, tk.END)


# ---------- GUI Setup ----------

root = tk.Tk()
root.title("Library Management System")
root.geometry("650x600")
root.configure(bg="#e3f2fd")

tk.Label(root, text="Book ID", bg="#e3f2fd").grid(row=0, column=0, padx=6, pady=6, sticky="w")
book_id = tk.Entry(root)
book_id.grid(row=0, column=1, padx=6, pady=6)

tk.Label(root, text="Title", bg="#e3f2fd").grid(row=1, column=0, padx=6, pady=6, sticky="w")
book_title = tk.Entry(root)
book_title.grid(row=1, column=1, padx=6, pady=6)

tk.Label(root, text="Author", bg="#e3f2fd").grid(row=2, column=0, padx=6, pady=6, sticky="w")
book_author = tk.Entry(root)
book_author.grid(row=2, column=1, padx=6, pady=6)

tk.Label(root, text="Quantity", bg="#e3f2fd").grid(row=3, column=0, padx=6, pady=6, sticky="w")
book_qty = tk.Entry(root)
book_qty.grid(row=3, column=1, padx=6, pady=6)

tk.Button(root, text="Add Book", command=add_book, width=12).grid(row=0, column=2, padx=6)
tk.Button(root, text="Display All", command=display_books, width=12).grid(row=1, column=2, padx=6)
tk.Button(root, text="Issue Book", command=issue_book, width=12).grid(row=2, column=2, padx=6)
tk.Button(root, text="Return Book", command=return_book, width=12).grid(row=3, column=2, padx=6)
tk.Button(root, text="Restock", command=restock_book, width=12).grid(row=4, column=2, padx=6)
tk.Button(root, text="Delete Book", command=delete_book, width=12).grid(row=5, column=2, padx=6)

tk.Label(root, text="Search Title", bg="#e3f2fd").grid(row=4, column=0, padx=6, pady=10, sticky="w")
search_entry = tk.Entry(root)
search_entry.grid(row=4, column=1, padx=6)
search_entry.bind("<Return>", lambda event: search_book())
tk.Button(root, text="Search", command=search_book, width=12).grid(row=5, column=0, padx=6, pady=4, sticky="w")

# Text area with monospace font (fixes column misalignment) + scrollbar
text_frame = tk.Frame(root)
text_frame.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

scrollbar = tk.Scrollbar(text_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text_box = tk.Text(text_frame, width=75, height=18, font=("Courier New", 10),
                   yscrollcommand=scrollbar.set)
text_box.pack(side=tk.LEFT, fill=tk.BOTH)
scrollbar.config(command=text_box.yview)

display_books()

root.mainloop()