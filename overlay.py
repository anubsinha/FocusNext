import tkinter as tk
from tkinter import ttk
import yaml
from datetime import datetime
import logging
from zoneinfo import ZoneInfo

logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Task Focus")
        self.local_tz = ZoneInfo("Asia/Kolkata")
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = 400  # Fixed width
        
        # Account for macOS menu bar
        menu_bar_height = 25
        usable_height = screen_height - menu_bar_height
        
        # Configure the window
        self.root.configure(bg='white')
        self.root.attributes('-topmost', True, '-alpha', 0.95)
        self.root.overrideredirect(True)
        
        # Position window below menu bar
        self.root.geometry(f'{width}x{usable_height}+{screen_width-width}+{menu_bar_height}')
        
        self.setup_ui(width)
        self.load_tasks()
        self.update_display()
        self.enforce_topmost()

    def setup_ui(self, width):
        # Main frame
        self.main_frame = tk.Frame(self.root, bg='white')
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=(20, 20))
        
        # Header section
        header_frame = tk.Frame(self.main_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 30))
        
        self.time_label = tk.Label(
            header_frame,
            text="",
            font=('SF Pro Display', 36, 'bold'),
            fg='#1a1a1a',
            bg='white'
        )
        self.time_label.pack(anchor='w')
        
        self.date_label = tk.Label(
            header_frame,
            text="",
            font=('SF Pro Display', 18),
            fg='#666666',
            bg='white'
        )
        self.date_label.pack(anchor='w')
        
        # Separator
        ttk.Separator(self.main_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Current task section
        current_frame = tk.Frame(self.main_frame, bg='white')
        current_frame.pack(fill='x', pady=20)
        
        tk.Label(
            current_frame,
            text="CURRENT TASK",
            font=('SF Pro Display', 14),
            fg='#666666',
            bg='white'
        ).pack(anchor='w')
        
        self.current_task_name = tk.Label(
            current_frame,
            text="",
            font=('SF Pro Display', 24, 'bold'),
            fg='#1a1a1a',
            bg='white',
            wraplength=width-40,
            justify='left'
        )
        self.current_task_name.pack(anchor='w', pady=(5, 0))
        
        self.current_task_desc = tk.Label(
            current_frame,
            text="",
            font=('SF Pro Display', 16),
            fg='#666666',
            bg='white',
            wraplength=width-40,
            justify='left'
        )
        self.current_task_desc.pack(anchor='w', pady=(5, 0))
        
        self.time_remaining = tk.Label(
            current_frame,
            text="",
            font=('SF Pro Display', 48, 'bold'),
            fg='#007AFF',
            bg='white'
        )
        self.time_remaining.pack(anchor='w', pady=(20, 0))
        
        # Separator
        ttk.Separator(self.main_frame, orient='horizontal').pack(fill='x', pady=20)
        
        # Next task section
        next_frame = tk.Frame(self.main_frame, bg='white')
        next_frame.pack(fill='x', pady=20)
        
        tk.Label(
            next_frame,
            text="UP NEXT",
            font=('SF Pro Display', 14),
            fg='#666666',
            bg='white'
        ).pack(anchor='w')
        
        self.next_task_name = tk.Label(
            next_frame,
            text="",
            font=('SF Pro Display', 24, 'bold'),
            fg='#1a1a1a',
            bg='white',
            wraplength=width-40,
            justify='left'
        )
        self.next_task_name.pack(anchor='w', pady=(5, 0))
        
        self.next_task_desc = tk.Label(
            next_frame,
            text="",
            font=('SF Pro Display', 16),
            fg='#666666',
            bg='white',
            wraplength=width-40,
            justify='left'
        )
        self.next_task_desc.pack(anchor='w', pady=(5, 0))
        
        self.next_task_time = tk.Label(
            next_frame,
            text="",
            font=('SF Pro Display', 24),
            fg='#007AFF',
            bg='white'
        )
        self.next_task_time.pack(anchor='w', pady=(10, 0))
        
        # Close button (top-right corner)
        self.close_button = tk.Button(
            self.root,
            text="×",
            command=self.root.quit,
            font=('SF Pro Display', 20),
            fg='#666666',
            bg='white',
            bd=0,
            highlightthickness=0
        )
        self.close_button.place(x=width-40, y=10)
        
        # Make window draggable
        self.root.bind('<Button-1>', self.start_drag)
        self.root.bind('<B1-Motion>', self.on_drag)

    def update_clock(self):
        now = datetime.now(self.local_tz)
        self.time_label.config(text=now.strftime("%I:%M %p"))
        self.date_label.config(text=now.strftime("%A, %B %d"))
        self.root.after(1000, self.update_clock)  # Update every second

    def enforce_topmost(self):
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, self.enforce_topmost)

    def load_tasks(self):
        try:
            with open('tasks.yaml', 'r') as file:
                self.tasks = yaml.safe_load(file)
                logger.info("Tasks loaded:")
                for task in self.tasks['tasks']:
                    logger.info(f"  {task['name']} - Schedule: {task['schedule']}")
        except Exception as e:
            logger.error(f"Error loading tasks: {e}")
            self.tasks = {'tasks': []}

    def parse_schedule(self, schedule):
        parts = schedule.split()
        # Return both minutes and hours
        return int(parts[0]), int(parts[1])  # minutes, hours

    def find_current_and_next_task(self):
        now = datetime.now(self.local_tz)
        current_hour = now.hour
        current_minute = now.minute
        
        current_task = None
        next_task = None
        
        for task in self.tasks['tasks']:
            task_minutes, task_hour = self.parse_schedule(task['schedule'])
            
            if current_hour == task_hour:
                minutes_elapsed = current_minute - task_minutes  # Account for task start minutes
                if minutes_elapsed >= 0 and minutes_elapsed < task['duration']:
                    current_task = {
                        'name': task['name'],
                        'description': task.get('description', ''),
                        'remaining': task['duration'] - minutes_elapsed
                    }
            
            if task_hour > current_hour or (task_hour == current_hour and task_minutes > current_minute):
                if next_task is None or (
                    task_hour < self.parse_schedule(next_task['schedule'])[1] or 
                    (task_hour == self.parse_schedule(next_task['schedule'])[1] and 
                     task_minutes < self.parse_schedule(next_task['schedule'])[0])
                ):
                    next_task = task
        
        if next_task:
            next_minutes, next_hour = self.parse_schedule(next_task['schedule'])
            next_time = now.replace(hour=next_hour, minute=next_minutes, second=0, microsecond=0)
            next_task = {
                'name': next_task['name'],
                'description': next_task.get('description', ''),
                'time': next_time
            }
        
        return current_task, next_task

    def update_display(self):
        current, next_task = self.find_current_and_next_task()
        
        if current:
            mins_remaining = max(0, int(current['remaining']))
            self.current_task_name.config(text=current['name'])
            self.current_task_desc.config(text=current['description'])
            self.time_remaining.config(text=f"{mins_remaining:02d}m")
        else:
            self.current_task_name.config(text="No current task")
            self.current_task_desc.config(text="")
            self.time_remaining.config(text="")
        
        if next_task:
            next_time_str = next_task['time'].strftime("%I:%M %p")
            self.next_task_name.config(text=next_task['name'])
            self.next_task_desc.config(text=next_task['description'])
            self.next_task_time.config(text=f"Starting at {next_time_str}")
        else:
            self.next_task_name.config(text="No upcoming tasks")
            self.next_task_desc.config(text="")
            self.next_task_time.config(text="")
        
        self.root.after(30000, self.update_display)

    def start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def on_drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def run(self):
        self.update_clock()  # Start the clock
        self.root.mainloop()

if __name__ == "__main__":
    app = TaskOverlay()
    app.run()
