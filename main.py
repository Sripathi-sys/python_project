from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView

class ToDoApp(App):
    def build(self):
        self.root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Task input field
        self.task_input = TextInput(hint_text="Enter a new task", size_hint_y=None, height=40)
        self.root.add_widget(self.task_input)

        # Add button
        add_button = Button(text="Add Task", size_hint_y=None, height=40)
        add_button.bind(on_press=self.add_task)
        self.root.add_widget(add_button)

        # Scrollable task list
        self.task_container = BoxLayout(orientation='vertical', size_hint_y=None)
        self.task_container.bind(minimum_height=self.task_container.setter('height'))
        
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.task_container)
        
        self.root.add_widget(scroll_view)

        return self.root

    def add_task(self, instance):
        task_text = self.task_input.text.strip()
        if task_text:
            task_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
            task_label = Label(text=task_text, size_hint_x=0.8, valign='middle')
            task_label.bind(size=task_label.setter('text_size'))

            delete_button = Button(text="X", size_hint_x=0.2)
            delete_button.bind(on_press=lambda btn: self.task_container.remove_widget(task_box))

            task_box.add_widget(task_label)
            task_box.add_widget(delete_button)

            self.task_container.add_widget(task_box)

            self.task_input.text = ""

ToDoApp().run()
