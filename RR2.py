import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import time

class RoundRobinSimulator:
    def __init__(self, root):
        # Inicializa la ventana principal y los parámetros de la simulación
        self.root = root
        self.root.title("Simulador Round Robin")
        self.quantum = 5         # Tiempo máximo que se le asigna a cada proceso en cada ciclo
        self.time = 0            # Tiempo global de la simulación
        self.processes = []      # Lista que almacenará los procesos
        self.gantt_chart_data = []  # Datos para el diagrama de Gantt
        self.semaphore = 1       # Semáforo: 1=Libre, 0=Ocupado (simula exclusión mutua)
        self.setup_ui()          # Configura la interfaz gráfica
    def setup_ui(self):
        # Marco principal
        main_frame = tk.Frame(self.root, bg="lightgray")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Marco izquierdo para la tabla
        left_frame = tk.Frame(main_frame, bg="lightgray")
        left_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Tabla de procesos
        self.tree = ttk.Treeview(
            left_frame,
            columns=("ID", "T. Llegada", "Ráfaga", "T. Comienzo", "T. Final", "T. Retorno", "T. Espera", "Estado", "Ejecución"),
            show="headings",
        )
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", width=50)
        self.tree.heading("T. Llegada", text="T. Llegada")
        self.tree.column("T. Llegada", width=80)
        self.tree.heading("Ráfaga", text="Ráfaga")
        self.tree.column("Ráfaga", width=80)
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

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Marco para gráfico de Gantt
        right_frame = tk.Frame(main_frame, bg="lightgray")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Gráfico de Gantt
        self.figure = Figure(figsize=(8, 7))
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Diagrama de Gantt")
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Procesos")
        self.ax.set_facecolor('lightgray')
        self.canvas = FigureCanvasTkAgg(self.figure, right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Marco para controles
        control_frame = tk.Frame(right_frame, bg="lightgray")
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Indicador de semáforo
        self.semaphore_label = tk.Label(control_frame, text="Semáforo: Libre", bg="green", fg="white", font=("Arial", 12))
        self.semaphore_label.pack(side=tk.TOP, fill=tk.X, pady=5)

        # Botones
        button_frame = tk.Frame(control_frame, bg="lightgray")
        button_frame.pack(fill=tk.X, pady=5)
        tk.Button(button_frame, text="Agregar Proceso", command=self.add_process).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Iniciar", command=self.start_simulation).pack(side=tk.LEFT, padx=5)
        
        
    def add_process(self):
        # Asigna un ID secuencial a cada proceso
        process_id = len(self.processes) + 1
        # Define el tiempo de llegada de cada proceso
        arrival_time = process_id - 1
        # Define el tiempo de ráfaga (burst) de manera aleatoria entre 5 y 15
        burst_time = random.randint(5, 15)
        # Se añade el proceso a la lista con sus parámetros iniciales
        self.processes.append({
            "id": process_id,
            "arrival": arrival_time,
            "burst": burst_time,
            "start": None,            # Tiempo en que el proceso inicia su ejecución
            "end": None,              # Tiempo en que finaliza la ejecución
            "turnaround": None,       # Tiempo total desde la llegada hasta el fin
            "waiting": None,          # Tiempo de espera en cola
            "remaining": burst_time,  # Tiempo restante de ejecución
            "state": "Listo",         # Estado inicial del proceso
            "executions": [],         # Lista para almacenar los intervalos de ejecución
            "block_time": 0,          # Tiempo que estará bloqueado (en caso de bloqueo)
            "total_executed": 0       # Tiempo ejecutado acumulado (opcional para cálculos)
        })
        # Se actualiza la tabla con la nueva información
        self.update_table()

    def update_table(self):
        # Elimina todos los elementos existentes en el Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Recorre cada proceso para mostrar su información
        for p in self.processes:
            # Valores principales de cada proceso
            main_values = (
                p["id"],
                p["arrival"],
                p["burst"],
                p["start"] or "-",  # Muestra "-" si aún no tiene valor
                p["end"] or "-",
                p["turnaround"] or "-",
                p["waiting"] or "-",
                p["state"],
                "Llegada" if not p["executions"] else "-"  # Muestra "Llegada" si no se ha ejecutado nada
            )
            self.tree.insert("", "end", values=main_values)
            
            # Se agregan sub-filas para cada intervalo de ejecución registrado
            for i, exec_data in enumerate(p["executions"]):
                # Calcula el tiempo de turnaround parcial para este segmento
                partial_turnaround = exec_data["end"] - p["arrival"]
                # Suma el tiempo ejecutado acumulado hasta el segmento actual
                executed_so_far = sum(
                    e["end"] - e["start"] 
                    for e in p["executions"][:i+1]
                )
                # Calcula el tiempo de espera parcial restando el tiempo ejecutado del turnaround
                partial_waiting = partial_turnaround - executed_so_far
                self.tree.insert("", "end", values=(
                    p["id"],
                    p["arrival"],
                    p["burst"],
                    exec_data["start"],
                    exec_data["end"],
                    partial_turnaround,
                    partial_waiting,
                    exec_data["state"],
                    exec_data["interval"]
                ))
        # Forzamos la actualización de la interfaz
        self.root.update_idletasks()

    def update_gantt_chart(self):
        # Limpia el eje para redibujar el diagrama de Gantt
        self.ax.clear()
        self.ax.set_title("Diagrama de Gantt")
        self.ax.set_xlabel("Tiempo")
        self.ax.set_ylabel("Procesos")
        self.ax.grid(axis="both", linestyle="--", linewidth=0.5, color="gray", alpha=0.7)

        # Se obtienen los IDs de los procesos para configurar el eje Y
        process_ids = sorted(set(data["id"] for data in self.gantt_chart_data))
        self.ax.set_yticks(process_ids)
        self.ax.set_yticklabels([f"Proceso {pid}" for pid in process_ids])

        # Se dibuja cada segmento de ejecución en el diagrama
        for process in self.gantt_chart_data:
            self.ax.broken_barh(
                [(process["start"], process["duration"])],
                (process["id"] - 0.4, 0.8),
                facecolors="tab:purple"
            )
        # Se actualiza el canvas para mostrar los cambios
        self.canvas.draw()

    def start_simulation(self):
        # Inicia la simulación llamando al método run_round_robin
        self.run_round_robin()

    def run_round_robin(self):
        # Verifica si todos los procesos han terminado (remaining <= 0)
        if all(p["remaining"] <= 0 for p in self.processes):
            return

        # Recorre cada proceso en la lista
        for process in self.processes:
            # Si el proceso aún tiene tiempo de ejecución pendiente
            if process["remaining"] > 0:
                # Si el proceso está bloqueado, decrementa su tiempo de bloqueo
                if process["state"] == "Bloqueado":
                    process["block_time"] -= 1
                    # Una vez finalizado el tiempo de bloqueo, el proceso pasa a estado "Listo"
                    if process["block_time"] <= 0:
                        process["state"] = "Listo"
                    self.update_table()
                    continue

                # Si es la primera vez que el proceso se ejecuta, se define el tiempo de inicio
                if process["start"] is None:
                    process["start"] = max(self.time, process["arrival"])

                # Se verifica si el semáforo está libre (valor 1)
                if self.semaphore == 1:
                    # Se toma el semáforo, indicándolo como ocupado (valor 0)
                    self.semaphore = 0
                    # Se actualiza la etiqueta del semáforo para mostrar el proceso que se está ejecutando
                    self.semaphore_label.config(text=f"Semáforo: Ocupado (Proceso {process['id']})", bg="red")
                    self.root.update_idletasks()

                    executed_time = 0  # Tiempo acumulado de ejecución en este quantum
                    execution_start = self.time  # Marca de tiempo de inicio de este ciclo de ejecución

                    # Se ejecuta el quantum para el proceso actual
                    for _ in range(self.quantum):
                        # Si el proceso ya terminó su ejecución, se sale del ciclo
                        if process["remaining"] <= 0:
                            break

                        # Se incrementa el tiempo ejecutado y global
                        executed_time += 1
                        self.time += 1
                        process["remaining"] -= 1  # Se decrementa el tiempo restante del proceso
                        
                        # Se actualizan la tabla y el diagrama de Gantt para visualizar el cambio
                        self.update_table()
                        self.update_gantt_chart()
                        self.root.update()  # Forzamos la actualización de la ventana
                        time.sleep(1)  # Se espera 1 segundo para visualizar la ejecución

                        # Se simula la posibilidad de que el proceso se bloquee (10% de probabilidad)
                        if random.random() < 0.1 and process["remaining"] > 0:
                            process["state"] = "Bloqueado"
                            # Se asigna un tiempo de bloqueo aleatorio entre 1 y 3 segundos
                            process["block_time"] = 1
                            break

                    # Se marca el final del quantum
                    execution_end = self.time
                    execution_state = process["state"]

                    # Si el proceso terminó de ejecutarse, se actualizan los tiempos finales y métricas
                    if process["remaining"] == 0:
                        execution_state = "Terminado"
                        process["end"] = self.time
                        process["turnaround"] = process["end"] - process["arrival"]
                        process["waiting"] = process["turnaround"] - process["burst"]

                    # Se registra el intervalo de ejecución en el proceso
                    process["executions"].append({
                        "interval": f"({execution_start}-{execution_end})",
                        "state": execution_state,
                        "start": execution_start,
                        "end": execution_end
                    })
                    
                    # Se almacena la información para el diagrama de Gantt
                    self.gantt_chart_data.append({
                        "id": process["id"], 
                        "start": execution_start, 
                        "duration": executed_time
                    })

                    # Se libera el semáforo, permitiendo que otro proceso se ejecute
                    self.semaphore = 1
                    self.semaphore_label.config(text="Semáforo: Libre", bg="green")
                    self.root.update_idletasks()

                    # Se actualizan nuevamente la tabla y el diagrama para reflejar los cambios finales
                    self.update_table()
                    self.update_gantt_chart()

        # Se programa la siguiente iteración de la simulación después de 1 segundo
        self.root.after(1000, self.run_round_robin)

if __name__ == "__main__":
    # Se crea la ventana principal de Tkinter y se inicia la simulación
    root = tk.Tk()
    app = RoundRobinSimulator(root)
    root.mainloop()
