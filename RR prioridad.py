import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import threading
import random

class RoundRobinSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador Round Robin")
        self.root.config(bg="gray")  # Cambia el color de fondo de la ventana principal a gris
        self.quantum = 5
        self.time = 0
        self.processes = []
        self.gantt_chart_data = []
        self.semaphore = 1

        # Configurar interfaz
        self.setup_ui()

    def setup_ui(self):
        # Marco principal
        main_frame = tk.Frame(self.root, bg="lightgray")  # o "gray" o "#D3D3D3" # Cambia el color de fondo del marco principal a gris
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Marco izquierdo para la tabla
        left_frame = tk.Frame(main_frame, bg="lightgray")  # Cambia el color de fondo del marco izquierdo a gris
        left_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Tabla de procesos
        self.tree = ttk.Treeview(
            left_frame,
            columns=("ID", "T. Llegada", "Ráfaga", "Prioridad", "T. Comienzo", "T. Final", "T. Retorno", "T. Espera", "Estado", "Ejecución"),
            show="headings",
        )
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=50)
        self.tree.heading("T. Llegada", text="T. Llegada")
        self.tree.column("T. Llegada", width=80)
        self.tree.heading("Ráfaga", text="Ráfaga")
        self.tree.column("Ráfaga", width=80)
        self.tree.heading("Prioridad", text="Prioridad")
        self.tree.column("Prioridad", width=80)
        self.tree.heading("T. Comienzo", text="T. Comienzo")
        self.tree.column("T. Comienzo", width=100)
        self.tree.heading("T. Final", text="T. Final")
        self.tree.column("T. Final", width=100)
        self.tree.heading("T. Retorno", text="T. Retorno")
        self.tree.column("T. Retorno", width=100)
        self.tree.heading("T. Espera", text="T. Espera")
        self.tree.column("T. Espera", width=100)
        self.tree.heading("Estado", text="Estado")
        self.tree.column("Estado", width=80)
        self.tree.heading("Ejecución", text="Ejecución")
        self.tree.column("Ejecución", width=250)

        # Modificar el color de fondo de la tabla (puedes cambiar el color para la fila seleccionada y la fila normal)
        self.tree.tag_configure('oddrow', background="lightgray")  # Fondo gris para filas impares
        self.tree.tag_configure('evenrow', background="lightgray")  # Fondo gris para filas pares

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Marco para controles y gráfico de Gantt (debajo de la tabla)
        bottom_frame = tk.Frame(main_frame, bg="lightgray")  # Cambia el color de fondo del marco inferior a gris
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Marco para gráfico de Gantt
        right_frame = tk.Frame(bottom_frame, bg="lightgray")  # Cambia el color de fondo del marco del gráfico a gris
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Gráfico de Gantt
        self.figure = Figure(figsize=(8, 7))
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Diagrama de Gantt")
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Procesos")
        self.ax.set_facecolor('lightgray')  # Fondo gris para el gráfico de Gantt
        self.canvas = FigureCanvasTkAgg(self.figure, right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Marco para controles y semáforo
        control_frame = tk.Frame(bottom_frame, bg="lightgray")  # Cambia el color de fondo del marco de controles a gris
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Indicador de semáforo
        self.semaphore_label = tk.Label(control_frame, text="Semáforo: Libre", bg="green", fg="white", font=("Arial", 12))
        self.semaphore_label.pack(side=tk.TOP, fill=tk.X, pady=5)

        # Botones de control
        button_frame = tk.Frame(control_frame, bg="lightgray")  # Cambia el color de fondo del marco de botones a gris
        button_frame.pack(fill=tk.X, pady=5)
        tk.Button(button_frame, text="Agregar Proceso", command=self.add_process).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Iniciar", command=self.start_simulation).pack(side=tk.LEFT, padx=5)

    def add_process(self):
        process_id = len(self.processes) + 1
        arrival_time = self.time
        burst_time = random.randint(5, 15)  # Duración aleatoria
        priority = random.randint(1, 5)  # Prioridad aleatoria (1 = más alta)
        self.processes.append({
            "id": process_id,
            "arrival": arrival_time,
            "burst": burst_time,
            "priority": priority,  # Asegúrate de agregar esta clave
            "start": None,
            "end": None,
            "turnaround": None,
            "waiting": None,
            "remaining": burst_time,
            "state": "Listo",
            "executions": []  # Añadir la clave "executions" como lista vacía
        })
        self.update_table()

    def update_table(self):
        # Usamos after() para asegurar que la actualización de la tabla se ejecute en el hilo principal
        self.root.after(0, self._update_table)

    def _update_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for i, p in enumerate(self.processes):
            execution_str = ", ".join(p["executions"]) if p["executions"] else "-"
            row_tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert(
                "",
                "end",
                values=(p["id"], p["arrival"], p["burst"], p["priority"], p["start"] if p["start"] is not None else "-",
                        p["end"] if p["end"] is not None else "-", p["turnaround"] if p["turnaround"] is not None else "-",
                        p["waiting"] if p["waiting"] is not None else "-", p["state"], execution_str),
                tags=(row_tag,)
            )


    def update_gantt_chart(self):
        self.ax.clear()
        self.ax.set_title("Diagrama de Gantt")
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Procesos")

        self.ax.grid(axis="both", linestyle="--", linewidth=0.5, color="lightgray", alpha=0.7)

        process_ids = sorted(set(data["id"] for data in self.gantt_chart_data))
        self.ax.set_yticks(process_ids)
        self.ax.set_yticklabels([f"Proceso {pid}" for pid in process_ids])

        for process in self.gantt_chart_data:
            self.ax.broken_barh(
                [(process["start"], process["duration"])],
                (process["id"] - 0.4, 0.8),
                facecolors="tab:purple"
            )

        self.canvas.draw()

    def start_simulation(self):
        threading.Thread(target=self.run_round_robin).start()
            
    def run_round_robin(self):
        while any(p["remaining"] > 0 for p in self.processes):
            self.processes.sort(key=lambda x: (x["priority"], x["arrival"]))

            for process in self.processes:
                if process["remaining"] > 0:
                    # Manejo de bloqueos
                    if process["state"] == "Bloqueado":
                        process["block_time"] -= 1
                        if process["block_time"] <= 0:
                            process["state"] = "Listo"
                        continue

                    # Control de semáforo
                    if self.semaphore == 1:
                        self.semaphore = 0
                        self.semaphore_label.config(text="Semáforo: Ocupado", bg="red")
                        self.root.update_idletasks()

                        if process["start"] is None:
                            process["start"] = max(self.time, process["arrival"])

                        executed_time = 0
                        execution_start = self.time  # Marcar inicio de la ejecución parcial

                        for _ in range(self.quantum):
                            if process["remaining"] <= 0:
                                break  # Si terminó, salir

                            time.sleep(1)  # Simula la ejecución en tiempo real
                            process["remaining"] -= 1
                            executed_time += 1
                            self.time += 1

                            # **Simular bloqueo aleatorio**
                            if random.random() < 0.1:  # 10% de probabilidad de bloqueo
                                process["state"] = "Bloqueado"
                                process["block_time"] = 0
                                break
                            

                        execution_end = self.time  # Marcar fin de la ejecución parcial

                        # **Actualizar el diagrama de Gantt**
                        self.gantt_chart_data.append({"id": process["id"], "start": execution_start, "duration": executed_time})

                        # **Registrar ejecución parcial en la columna "Ejecución"**
                        process["executions"].append(f" ({execution_start}-{execution_end})")

                        # Si terminó, actualizar tiempos
                        if process["remaining"] == 0:
                            process["end"] = self.time
                            process["turnaround"] = process["end"] - process["arrival"]
                            process["waiting"] = process["turnaround"] - process["burst"]
                            process["state"] = "Terminado"
                        elif process["state"] != "Bloqueado":  # Si no terminó ni se bloqueó, sigue en "Listo"
                            process["state"] = "Listo"

                        # Liberar semáforo
                        self.semaphore = 1
                        self.semaphore_label.config(text="Semáforo: Libre", bg="green")

                        # **Actualizar la tabla y el gráfico**
                        self.update_table()
                        self.update_gantt_chart()


# Ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = RoundRobinSimulator(root)
    root.mainloop()
