from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import fitz  # PyMuPDF
import time

class PDFWordReaderApp(App):
    def build(self):
        # Define adjustable values and scores
        self.settings = {
            'speed': 1.0,
            'font_size_top': 32,
            'font_size_bottom': 24,
            'text_color': (1, 1, 1, 1)
        }
        self.score = 0
        self.reading_start_time = None
        self.reading_statistics = {
            'total_time': 0,
            'total_words': 0,
            'topic_count': {}
        }
        self.word_index = 0
        self.word_list = []
        self.qa_questions = []

        # Top panel: displays words one by one
        self.top_panel = Label(text='', font_size=self.settings['font_size_top'], color=self.settings['text_color'])

        # Bottom panel: displays the entire sentence with current word highlighted
        self.bottom_panel = Label(text='', font_size=self.settings['font_size_bottom'], color=self.settings['text_color'])

        # Score label
        self.score_label = Label(text=f"Score: {self.score}")

        # Speed control slider
        self.speed_slider = Slider(min=0.1, max=2.0, value=self.settings['speed'])
        self.speed_slider.bind(value=self.update_speed)

        # Color picker for text color customization
        self.color_picker = ColorPicker()
        self.color_picker.bind(color=self.on_color)

        # Font size adjustment buttons
        increase_font_size_btn = Button(text="Increase Font Size")
        increase_font_size_btn.bind(on_press=self.increase_font_size)
        
        decrease_font_size_btn = Button(text="Decrease Font Size")
        decrease_font_size_btn.bind(on_press=self.decrease_font_size)

        # File chooser button
        file_chooser_btn = Button(text="Choose PDF")
        file_chooser_btn.bind(on_press=self.show_file_chooser)

        # Settings button
        settings_btn = Button(text="Settings")
        settings_btn.bind(on_press=self.show_settings)

        # QA button
        qa_btn = Button(text="QA")
        qa_btn.bind(on_press=self.show_qa)

        # Task planner button
        task_planner_btn = Button(text="Task Planner")
        task_planner_btn.bind(on_press=self.show_task_planner)

        # Layout setup
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(file_chooser_btn)
        layout.add_widget(settings_btn)
        layout.add_widget(self.score_label)
        layout.add_widget(self.top_panel)
        layout.add_widget(self.bottom_panel)
        layout.add_widget(self.speed_slider)
        layout.add_widget(self.color_picker)
        layout.add_widget(increase_font_size_btn)
        layout.add_widget(decrease_font_size_btn)
        layout.add_widget(qa_btn)
        layout.add_widget(task_planner_btn)
        
        return layout

    def show_file_chooser(self, instance):
        # Show file chooser to select a PDF file
        filechooser = FileChooserIconView(filters=['*.pdf'])
        filechooser.bind(on_submit=self.load_pdf)

        self.root.clear_widgets()
        self.root.add_widget(filechooser)

    def load_pdf(self, filechooser, selection, touch):
        # Load the selected PDF file
        if selection:
            self.word_list = self.extract_words_from_pdf(selection[0])
            self.word_index = 0

            # Start tracking reading time
            self.reading_start_time = time.time()

            self.root.clear_widgets()
            self.build()
            Clock.schedule_interval(self.display_next_word, 1.0 / self.settings['speed'])

    def extract_words_from_pdf(self, file_path):
        # Extract text from PDF and split it into words
        document = fitz.open(file_path)
        text = ''
        for page in document:
            text += page.get_text()
        words = text.split()
        return words
    
    def update_speed(self, instance, value):
        # Update the speed of word appearance
        self.settings['speed'] = value
        Clock.unschedule(self.display_next_word)
        Clock.schedule_interval(self.display_next_word, 1.0 / self.settings['speed'])

    def on_color(self, instance, value):
        # Change text color
        self.settings['text_color'] = value
        self.top_panel.color = value
        self.bottom_panel.color = value

    def increase_font_size(self, instance):
        # Increase the font size of the text
        self.settings['font_size_top'] += 2
        self.settings['font_size_bottom'] += 2
        self.top_panel.font_size = self.settings['font_size_top']
        self.bottom_panel.font_size = self.settings['font_size_bottom']

    def decrease_font_size(self, instance):
        # Decrease the font size of the text
        self.settings['font_size_top'] -= 2
        self.settings['font_size_bottom'] -= 2
        self.top_panel.font_size = self.settings['font_size_top']
        self.bottom_panel.font_size = self.settings['font_size_bottom']

    def display_next_word(self, dt):
        # Display the next word and update the sentence view
        if self.word_index < len(self.word_list):
            current_word = self.word_list[self.word_index]
            self.top_panel.text = current_word
            sentence = " ".join(self.word_list[:self.word_index+1])
            self.bottom_panel.text = sentence
            self.word_index += 1
            self.score += 1
            self.score_label.text = f"Score: {self.score}"
        else:
            Clock.unschedule(self.display_next_word)
            total_reading_time = time.time() - self.reading_start_time
            self.reading_statistics['total_time'] += total_reading_time
            self.reading_statistics['total_words'] += self.word_index
            self.reading_start_time = None
            print("Reading Statistics:", self.reading_statistics)

    def show_settings(self, instance):
        # Create a popup for settings
        layout = GridLayout(cols=2, padding=10)

        # Speed setting
        layout.add_widget(Label(text='Speed'))
        speed_input = TextInput(text=str(self.settings['speed']))
        layout.add_widget(speed_input)

        # Font size setting for top panel
        layout.add_widget(Label(text='Font Size (Top Panel)'))
        font_size_top_input = TextInput(text=str(self.settings['font_size_top']))
        layout.add_widget(font_size_top_input)

        # Font size setting for bottom panel
        layout.add_widget(Label(text='Font Size (Bottom Panel)'))
        font_size_bottom_input = TextInput(text=str(self.settings['font_size_bottom']))
        layout.add_widget(font_size_bottom_input)

        # Save button
        save_btn = Button(text='Save')
        save_btn.bind(on_press=lambda x: self.save_settings(speed_input.text, font_size_top_input.text, font_size_bottom_input.text))
        layout.add_widget(save_btn)

        # Close button
        close_btn = Button(text='Close')
        close_btn.bind(on_press=lambda x: self.popup.dismiss())
        layout.add_widget(close_btn)

        self.popup = Popup(title='Settings', content=layout, size_hint=(0.9, 0.9))
        self.popup.open()

    def save_settings(self, speed, font_size_top, font_size_bottom):
        # Update settings based on user input
        self.settings['speed'] = float(speed)
        self.settings['font_size_top'] = int(font_size_top)
        self.settings['font_size_bottom'] = int(font_size_bottom)

        # Apply new settings
        self.speed_slider.value = self.settings['speed']
        self.top_panel.font_size = self.settings['font_size_top']
        self.bottom_panel.font_size = self.settings['font_size_bottom']

        self.popup.dismiss()

    def show_qa(self, instance):
        # Generate different types of QA questions based on the text
        if not self.qa_questions:
            self.qa_questions = self.generate_qa_questions()

        if self.qa_questions:
            question, answer = self.qa_questions.pop(0)
            self.display_question(question, answer)

    def generate_qa_questions(self):
        # Placeholder: Generate different types of QA questions from the text
        # Modify this method to suit your specific logic for generating questions
        questions = []
        
        # Insight related questions
        questions.append(("Give me insights related to this chapter's topic.", "Insightful answer"))
        
        # Challenge related questions
        questions.append(("What challenges might be faced regarding this topic?", "Challenging answer"))
        
        # Worth note related questions
        questions.append(("What points are worth noting about this topic?", "Noteworthy answer"))
        
        # Multiple point of view related questions
        questions.append(("Describe this topic from multiple points of view.", "Multi-faceted answer"))
        
        # Different ask related questions
        questions.append(("How else could you ask about this topic?", "Alternative answer"))
        
        # Better choice of word related questions
        questions.append(("How should I ask about this topic using better word choices?", "Improved answer"))
        
        # Deeper understanding related questions
        questions.append(("
