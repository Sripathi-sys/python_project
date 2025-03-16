from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.menu import MDDropdownMenu
from kivy.garden.matplotlib import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from database import Database

KV = """
ScreenManager:
    ToDoScreen:
    ExpenseScreen:

<ToDoScreen>:
    name: "todo"
    BoxLayout:
        orientation: "vertical"

        MDToolbar:
            title: "To-Do List"
            md_bg_color: app.theme_cls.primary_color
            specific_text_color: 1, 1, 1, 1
            left_action_items: [["menu", lambda x: app.change_screen("expense")]]
            right_action_items: [["theme-light-dark", lambda x: app.toggle_theme()]]

        ScrollView:
            MDList:
                id: task_list

        MDFloatLayout:
            MDTextField:
                id: task_input
                hint_text: "Enter task"
                size_hint_x: 0.8
                pos_hint: {"center_x": 0.5, "center_y": 0.1}
            
            MDRaisedButton:
                text: "Add Task"
                size_hint_x: 0.3
                pos_hint: {"center_x": 0.5, "center_y": 0.02}
                on_release: app.add_task()

<ExpenseScreen>:
    name: "expense"
    BoxLayout:
        orientation: "vertical"

        MDToolbar:
            title: "Expense Tracker"
            md_bg_color: app.theme_cls.primary_color
            specific_text_color: 1, 1, 1, 1
            left_action_items: [["arrow-left", lambda x: app.change_screen("todo")]]
            right_action_items: [["theme-light-dark", lambda x: app.toggle_theme()]]

        BoxLayout:
            size_hint_y: None
            height: "50dp"

            MDRaisedButton:
                text: "Filter by Category"
                on_release: app.show_category_menu(self)
                size_hint_x: 0.4
                pos_hint: {"x": 0.05}

            MDLabel:
                id: total_expense
                text: "Total Expenses: ₹0"
                halign: "center"
                font_style: "H5"

        ScrollView:
            MDList:
                id: expense_list

        BoxLayout:
            orientation: "vertical"
            size_hint_y: 0.4
            canvas.before:
                Color:
                    rgba: app.theme_cls.bg_normal
                Rectangle:
                    pos: self.pos
                    size: self.size
            id: chart_area

        MDFloatLayout:
            MDTextField:
                id: expense_amount
                hint_text: "Enter amount"
                size_hint_x: 0.4
                pos_hint: {"x": 0.05, "center_y": 0.1}
            
            MDTextField:
                id: expense_category
                hint_text: "Category"
                size_hint_x: 0.4
                pos_hint: {"x": 0.55, "center_y": 0.1}
            
            MDRaisedButton:
                text: "Add Expense"
                size_hint_x: 0.3
                pos_hint: {"center_x": 0.5, "center_y": 0.02}
                on_release: app.add_expense()
"""

class ToDoScreen(Screen):
    pass

class ExpenseScreen(Screen):
    pass

class ToDoApp(MDApp):
    def build(self):
        self.db = Database()
        self.theme_cls.theme_style = "Light"
        self.category_filter = None
        return Builder.load_string(KV)

    def on_start(self):
        """Load tasks and expenses when the app starts"""
        self.load_tasks()
        self.load_expenses()

    def change_screen(self, screen_name):
        """Switch between screens"""
        self.root.current = screen_name

    def toggle_theme(self):
        """Toggle between Light and Dark Mode"""
        if self.theme_cls.theme_style == "Light":
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"

    # To-Do List Functions
    def load_tasks(self):
        self.root.get_screen("todo").ids.task_list.clear_widgets()
        tasks = self.db.get_tasks()
        for task in tasks:
            self.add_task_item(task)

    def add_task(self):
        task_input = self.root.get_screen("todo").ids.task_input
        task_text = task_input.text.strip()
        if task_text:
            self.db.add_task(task_text)
            task_input.text = ""  
            self.load_tasks()  

    def add_task_item(self, task):
        task_id, task_text, completed = task
        item = OneLineAvatarIconListItem(text=task_text)
        delete_icon = IconLeftWidget(icon="delete")
        delete_icon.bind(on_release=lambda x: self.delete_task(task_id))
        item.add_widget(delete_icon)
        self.root.get_screen("todo").ids.task_list.add_widget(item)

    def delete_task(self, task_id):
        self.db.delete_task(task_id)
        self.load_tasks()

    # Expense Tracker Functions
    def load_expenses(self):
        self.root.get_screen("expense").ids.expense_list.clear_widgets()
        expenses = self.db.get_expenses()

        # Apply category filter
        if self.category_filter:
            expenses = [exp for exp in expenses if exp[2] == self.category_filter]

        total_expense = sum(exp[1] for exp in expenses)
        self.root.get_screen("expense").ids.total_expense.text = f"Total Expenses: ₹{total_expense}"

        for expense in expenses:
            self.add_expense_item(expense)

        self.update_expense_pie_chart()  # Update the pie chart

    def add_expense(self):
        amount_input = self.root.get_screen("expense").ids.expense_amount
        category_input = self.root.get_screen("expense").ids.expense_category

        try:
            amount = float(amount_input.text.strip())
            category = category_input.text.strip()
            if amount > 0 and category:
                self.db.add_expense(amount, category)
                amount_input.text = ""
                category_input.text = ""
                self.load_expenses()
        except ValueError:
            pass  

    def add_expense_item(self, expense):
        expense_id, amount, category, date = expense
        item = OneLineAvatarIconListItem(text=f"₹{amount} - {category} ({date})")
        delete_icon = IconLeftWidget(icon="delete")
        delete_icon.bind(on_release=lambda x: self.delete_expense(expense_id))
        item.add_widget(delete_icon)
        self.root.get_screen("expense").ids.expense_list.add_widget(item)

    def delete_expense(self, expense_id):
        self.db.delete_expense(expense_id)
        self.load_expenses()

    def show_category_menu(self, button):
        """Show a dropdown menu with expense categories"""
        categories = list(set(exp[2] for exp in self.db.get_expenses()))
        menu_items = [{"text": cat, "on_release": lambda x=cat: self.filter_by_category(x)} for cat in categories]
        menu_items.append({"text": "All", "on_release": lambda x=None: self.filter_by_category(x)})
        self.menu = MDDropdownMenu(items=menu_items, width_mult=3)
        self.menu.open()

    def filter_by_category(self, category):
        """Filter expenses by category"""
        self.category_filter = category
        self.menu.dismiss()
        self.load_expenses()

    def update_expense_pie_chart(self):
        """Generate a pie chart of expenses"""
        expenses = self.db.get_expenses()
        categories = {}
        for expense in expenses:
            _, amount, category, _ = expense
            categories[category] = categories.get(category, 0) + amount

        if not categories:
            return  

        labels = list(categories.keys())
        values = list(categories.values())

        plt.clf()
        plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=140)
        plt.axis("equal")

        chart_area = self.root.get_screen("expense").ids.chart_area
        chart_area.clear_widgets()
        chart_area.add_widget(FigureCanvasKivyAgg(plt.gcf()))

if __name__ == "__main__":
    ToDoApp().run()


import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

def update_expense_pie_chart(self):
    expenses = self.db.get_expenses()
    if not expenses:
        return  

    category_totals = {}
    for expense in expenses:
        category = expense[2]
        amount = expense[1]
        category_totals[category] = category_totals.get(category, 0) + amount

    labels = category_totals.keys()
    sizes = category_totals.values()

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90, colors=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"])
    ax.axis("equal")

    self.root.get_screen("expense").ids.chart.clear_widgets()
    self.root.get_screen("expense").ids.chart.add_widget(FigureCanvasKivyAgg(fig))
from kivymd.uix.selectioncontrol import MDCheckbox

def add_task_item(self, task):
    task_id, task_text = task
    item = OneLineAvatarIconListItem(text=task_text)

    checkbox = MDCheckbox()
    checkbox.bind(active=lambda checkbox, value: self.complete_task(task_id, value))

    item.add_widget(checkbox)
    self.root.get_screen("todo").ids.task_list.add_widget(item)

def complete_task(self, task_id, is_checked):
    if is_checked:
        self.db.delete_task(task_id)
        self.load_tasks()
import csv

def export_data(self):
    with open("exported_data.csv", "w", newline="") as file:
        writer = csv.writer(file)
        
        writer.writerow(["Tasks"])
        for task in self.db.get_tasks():
            writer.writerow([task[1]])

        writer.writerow([])
        writer.writerow(["Expenses"])
        for expense in self.db.get_expenses():
            writer.writerow([expense[1], expense[2], expense[3]])

    print("Data exported to exported_data.csv")
from kivymd.uix.picker import MDDatePicker
from datetime import datetime

class ToDoApp(MDApp):
    def build(self):
        # Your existing build method
        pass

    def show_date_picker(self):
        date_dialog = MDDatePicker(
            callback=self.on_date_selected,
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day
        )
        date_dialog.open()

    def on_date_selected(self, date):
        self.selected_date = date
        print(f"Selected date: {self.selected_date}")
class ToDoApp(MDApp):
    def build(self):
        # Your existing build method
        pass

    def calculate_total_expenses(self):
        expenses = self.db.get_expenses()
        total = sum(expense[1] for expense in expenses)
        self.root.get_screen("expense").ids.total_expenses.text = f"Total Expenses: ₹{total}"

