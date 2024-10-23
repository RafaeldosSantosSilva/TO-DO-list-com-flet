import flet as ft
from datetime import datetime
import json
import os

class TodoApp(ft.UserControl):
    def __init__(self):
        super().__init__()
        # Cores modernas
        self.colors = {
            "background": "#1A1B26",  # Fundo escuro elegante
            "card": "#24283B",        # Cor do card/container
            "primary": "#7AA2F7",     # Azul principal
            "secondary": "#BB9AF7",   # Roxo secundário
            "text": "#A9B1D6",        # Texto principal
            "success": "#9ECE6A",     # Verde para tarefas concluídas
            "error": "#F7768E",       # Vermelho para ações de deletar
            "warning": "#E0AF68"      # Laranja para edição
        }
        self.new_task = ft.TextField(
            hint_text="Adicionar nova tarefa...",
            expand=True,
            height=50,
            border_radius=8,
            bgcolor=self.colors["card"],
            color=self.colors["text"],
            border_color=self.colors["primary"]
        )
        self.tasks = []
        self.filter = "all"
        self.tasks_view = ft.Column()
        self.json_file = "tasks.json"
        self.load_tasks()

    def load_tasks(self):
        """Carrega as tarefas do arquivo JSON."""
        if os.path.exists(self.json_file):
            try:
                with open(self.json_file, 'r', encoding='utf-8') as file:
                    tasks_data = json.load(file)
                    for task_data in tasks_data:
                        task = Task(
                            task_data['name'],
                            self.task_status_changed,
                            self.task_delete,
                            self.colors
                        )
                        task.completed = task_data['completed']
                        self.tasks.append(task)
            except json.JSONDecodeError:
                print("Erro ao ler o arquivo JSON. Criando nova lista.")

    def save_tasks(self):
        """Salva as tarefas em um arquivo JSON."""
        tasks_data = [
            {
                'name': task.task_name,
                'completed': task.completed,
                'created_at': datetime.now().isoformat()
            }
            for task in self.tasks
        ]
        with open(self.json_file, 'w', encoding='utf-8') as file:
            json.dump(tasks_data, file, ensure_ascii=False, indent=2)

    def build(self):
        self.filter_buttons = ft.Row(
            controls=[
                ft.TextButton(
                    text="Todas",
                    on_click=lambda e: self.filter_tasks("all"),
                    style=ft.ButtonStyle(color=self.colors["text"]),
                ),
                ft.TextButton(
                    text="Ativas",
                    on_click=lambda e: self.filter_tasks("active"),
                    style=ft.ButtonStyle(color=self.colors["text"]),
                ),
                ft.TextButton(
                    text="Concluídas",
                    on_click=lambda e: self.filter_tasks("completed"),
                    style=ft.ButtonStyle(color=self.colors["text"]),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            self.new_task,
                            ft.IconButton(
                                icon=ft.icons.ADD_CIRCLE_ROUNDED,
                                icon_color=self.colors["primary"],
                                on_click=self.add_task,
                                icon_size=40,
                            ),
                        ],
                    ),
                    self.filter_buttons,
                    self.tasks_view,
                ],
            ),
            padding=20,
            bgcolor=self.colors["background"],
        )

    def add_task(self, e):
        if self.new_task.value:
            task = Task(
                self.new_task.value,
                self.task_status_changed,
                self.task_delete,
                self.colors
            )
            self.tasks.append(task)
            self.new_task.value = ""
            self.update_tasks_view()
            self.save_tasks()  # Salva após adicionar
            self.new_task.focus()
            self.update()

    def task_status_changed(self, task):
        self.update_tasks_view()
        self.save_tasks()  # Salva após mudar status
        self.update()

    def task_delete(self, task):
        self.tasks.remove(task)
        self.update_tasks_view()
        self.save_tasks()  # Salva após deletar
        self.update()

    def filter_tasks(self, filter_status):
        self.filter = filter_status
        self.update_tasks_view()
        self.update()

    def update_tasks_view(self):
        filtered_tasks = self.tasks
        if self.filter == "active":
            filtered_tasks = [task for task in self.tasks if not task.completed]
        elif self.filter == "completed":
            filtered_tasks = [task for task in self.tasks if task.completed]
        
        self.tasks_view.controls = [
            task for task in filtered_tasks
        ]

class Task(ft.UserControl):
    def __init__(self, task_name, status_changed, task_delete, colors):
        super().__init__()
        self.task_name = task_name
        self.status_changed = status_changed
        self.task_delete = task_delete
        self.completed = False
        self.colors = colors
        self.editing = False
        self.task_edit_field = ft.TextField(
            value=self.task_name,
            expand=True,
            bgcolor=self.colors["card"],
            color=self.colors["text"],
            border_color=self.colors["warning"]
        )

    def build(self):
        self.display_task = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Checkbox(
                    value=self.completed,
                    on_change=self.status_changed_click,
                    fill_color=self.colors["success"],
                ),
                ft.Text(
                    self.task_name,
                    color=self.colors["text"],
                    style=ft.TextStyle(
                        decoration=ft.TextDecoration.LINE_THROUGH
                        if self.completed
                        else ft.TextDecoration.NONE,
                    ),
                    size=16,
                ),
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.EDIT_ROUNDED,
                            icon_color=self.colors["warning"],
                            on_click=self.edit_clicked,
                            tooltip="Editar",
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE_ROUNDED,
                            icon_color=self.colors["error"],
                            on_click=self.delete_clicked,
                            tooltip="Excluir",
                        ),
                    ]
                ),
            ],
        )

        self.editing_task = ft.Row(
            visible=False,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.task_edit_field,
                ft.IconButton(
                    icon=ft.icons.DONE_ROUNDED,
                    icon_color=self.colors["success"],
                    on_click=self.save_clicked,
                    tooltip="Salvar",
                ),
            ],
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    self.display_task,
                    self.editing_task,
                ]
            ),
            bgcolor=self.colors["card"],
            padding=12,
            border_radius=8,
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )

    def edit_clicked(self, e):
        self.editing = True
        self.display_task.visible = False
        self.editing_task.visible = True
        self.task_edit_field.value = self.task_name
        self.update()

    def save_clicked(self, e):
        self.task_name = self.task_edit_field.value
        self.editing = False
        self.display_task.controls[1].value = self.task_name
        self.display_task.visible = True
        self.editing_task.visible = False
        self.status_changed(self)  # Salva após editar
        self.update()

    def status_changed_click(self, e):
        self.completed = self.display_task.controls[0].value
        self.display_task.controls[1].style.decoration = (
            ft.TextDecoration.LINE_THROUGH
            if self.completed
            else ft.TextDecoration.NONE
        )
        self.status_changed(self)

    def delete_clicked(self, e):
        self.task_delete(self)

def main(page: ft.Page):
    page.bgcolor = "#1A1B26"
    page.title = "Todo App Moderno"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()

    todo = TodoApp()
    page.add(todo)

ft.app(target=main)