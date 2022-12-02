import tkinter.messagebox
from turtle import bgcolor
from matplotlib.pyplot import grid, text
import numpy as np
import random as rnd
from threading import Thread
import time
import tkinter
import customtkinter
import random
import copy

# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("System")
# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("blue")


# Améliorations : 
# GUI : mettre un bouton reset
# Si jamais reject, voir si on peut quand même bouger ailleurs
# Si jamais deux chemins égaux privilégier celui sans REQUEST
# Si freeCell, voir si notre nextPos était possible quand même
# Garder un historique des messages et changer le comportement si on a un cycle


def dist(x, y):
    return abs(x[0]-y[0]) + abs(x[1]-y[1])


class Message:
    def __init__(self, _type, _id_src, _id_dst):
        # REJECT, REQUEST, OK
        self.type = _type
        # self.content = ""
        self.id_src = _id_src
        self.id_dst = _id_dst


class Agent:

    def __init__(self, _id, init_pos, _goal):
        self.id = _id
        self.pos = init_pos
        self.goal = _goal
        self.done = False
        self.received_messages = []

    def move(self, x):
        self.pos = x
        self.done = (self.pos == self.goal)

    def send(self, message : Message, other):
        print("L'agent " + str(message.id_src) + " a envoyé un " + str(message.type) + " à l'agent " + str(message.id_dst))
        other.received_messages.append(message)

    def readMessage(self):
        return self.received_messages.pop(0)            
    
    def hasMessage(self):
        return not(len(self.received_messages) == 0)


class Taquin:

    def __init__(self, _grid_size: int, _nbr_agents: int):

        self.grid_size = _grid_size
        self.nbr_agents = _nbr_agents
        self.cells = [[-1 for col in range(self.grid_size)]
                      for lines in range(self.grid_size)]
        self.goals = [[-1 for col in range(self.grid_size)]
                      for lines in range(self.grid_size)]
        self.agents = {}
        self.end = False

        random_pos = []
        random_goal = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                random_pos.append((i, j))
                random_goal.append((i, j))

        random.shuffle(random_pos)
        random.shuffle(random_goal)

        for i in range(self.nbr_agents):
            self.agents[i] = Agent(i, random_pos[i], random_goal[i])
            self.cells[random_pos[i][0]][random_pos[i][1]] = i
            self.goals[self.agents[i].goal[0]][self.agents[i].goal[1]] = i

    def reset(self):
        self.cells = [[-1 for col in range(self.grid_size)]
                      for lines in range(self.grid_size)]
        self.goals = [[-1 for col in range(self.grid_size)]
                      for lines in range(self.grid_size)]
        self.agents = {}

        random_pos = []
        random_goal = []
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                random_pos.append((i, j))
                random_goal.append((i, j))

        random.shuffle(random_pos)
        random.shuffle(random_goal)

        for i in range(self.nbr_agents):
            self.agents[i] = Agent(i, random_pos[i], random_goal[i])
            self.cells[random_pos[i][0]][random_pos[i][1]] = i
            self.goals[self.agents[i].goal[0]][self.agents[i].goal[1]] = i

    def hasEnded(self):
        for agent in self.agents.values():
            if not agent.done:
                return False
        return True

    # Prochaine frame : 
    # Donner les intentions de mouvements de chacun
    # Etablir les communications si besoin
    # Répondre aux communications et update la position des concernés
    # Définir le mouvement final
    # Bouger
    def nextState(self):
        next_moves = {}
        
        # Calculer les intentions de mouvement de chacun
        for agent in self.agents.values():
            if(not agent.done):
                dists = list(self.nextPos(agent).values())
                moves = list(self.nextPos(agent).keys())
                tmp = moves[0]

                if(not tmp in next_moves.values()):
                    if(self.cells[tmp[0]][tmp[1]] != -1):
                        if(dists[0] == dists[1] and self.cells[moves[1][0]][moves[1][1]] == -1 and not moves[1] in next_moves.values()):
                            tmp = moves[1]

                next_moves[agent.id] = tmp
                

        # Etablir les communications si besoin    
        for id in next_moves.keys():
            next_pos = next_moves[id]
            id_other = self.cells[next_pos[0]][next_pos[1]]
            if(id_other != -1):
                waiting = False
                next_moves[id] = self.agents[id].pos

                for msg in self.agents[id].received_messages:
                    if msg.id_src == id_other:
                        waiting = True
                if(not waiting):
                    msg = Message("REQUEST", id, id_other)
                    self.agents[id].send(msg, self.agents[id_other])
                

        # Pour ceux qui ont reçu un message, voir s'ils peuvent libérer la case
        for agent in self.agents.values():
            already_moved = False
            while(agent.hasMessage()):
                msg = agent.readMessage()
                id_other = msg.id_src

                if(msg.type == "REQUEST"):
                    next_pos = self.freeCell(agent, next_moves.values())

                    if(next_pos != agent.pos and (not already_moved) and (not next_pos in next_moves.values())):
                        msg = Message("OK", agent.id, id_other)
                        next_moves[agent.id] = next_pos
                        already_moved = True
                    else:
                        msg = Message("REJECT", agent.id, id_other)
                        
                    agent.send(msg, self.agents[id_other])

                elif(msg.type == "REJECT" and not already_moved):
                    next_moves[agent.id] = self.agents[agent.id].pos
                    already_moved = True
                
                elif(msg.type == "OK" and not already_moved):
                    #ICI !!!!
                    next_moves[agent.id] = self.agents[id_other].pos
                    already_moved = True
                    
        
        # Définir le mouvement final en fonction des réponses
        # REJECT = on ne bouge pas
        # OK = on peut aller sur la case
        # for id in next_moves.keys():
        #     if(self.agents[id].hasMessage()):
        #         msg = self.agents[id].readMessage()
        #         if(msg.type == "REJECT"):
        #             next_moves[id] = self.agents[id].pos

        # Update la grille
        for id in next_moves.keys():
            if(self.cells[self.agents[id].pos[0]][self.agents[id].pos[1]] == id):
                self.cells[self.agents[id].pos[0]][self.agents[id].pos[1]] = -1

            self.agents[id].move(next_moves[id])
            self.cells[next_moves[id][0]][next_moves[id][1]] = id

        return self.cells

    def nextPos(self, agent: Agent):
        moves = {}

        if(agent.pos[1] < self.grid_size - 1):
            new_pos = tuple(np.add(agent.pos, (0, 1)))
            d = dist(new_pos, agent.goal)
            moves[new_pos] = d

        if(agent.pos[0] < self.grid_size - 1):
            new_pos = tuple(np.add(agent.pos, (1, 0)))
            d = dist(new_pos, agent.goal)
            moves[new_pos] = d

        if(agent.pos[1] > 0):
            new_pos = tuple(np.subtract(agent.pos, (0, 1)))
            d = dist(new_pos, agent.goal)
            moves[new_pos] = d

        if(agent.pos[0] > 0):
            new_pos = tuple(np.subtract(agent.pos, (1, 0)))
            d = dist(new_pos, agent.goal)
            moves[new_pos] = d

        sorted_moves = {k: v for k, v in sorted(moves.items(), key=lambda item: item[1])}

        return sorted_moves 
        
    def moveAgent(self, agent, pos):
        self.cells[agent.pos[0]][agent.pos[1]] = -1
        agent.move(pos)
        self.cells[pos[0]][pos[1]] = agent.id


    def freeCell(self, agent: Agent, next_moves):
        moves = {}

        if(agent.pos[1] < self.grid_size - 1):
            new_pos = tuple(np.add(agent.pos, (0, 1)))
            if(self.cells[new_pos[0]][new_pos[1]] == -1 and not(new_pos in next_moves)):
                d = dist(new_pos, agent.goal)
                moves[new_pos] = d

        if(agent.pos[0] < self.grid_size - 1):
            new_pos = tuple(np.add(agent.pos, (1, 0)))
            if(self.cells[new_pos[0]][new_pos[1]] == -1 and not(new_pos in next_moves)):
                d = dist(new_pos, agent.goal)
                moves[new_pos] = d

        if(agent.pos[1] > 0):
            new_pos = tuple(np.subtract(agent.pos, (0, 1)))
            if(self.cells[new_pos[0]][new_pos[1]] == -1 and not(new_pos in next_moves)):
                d = dist(new_pos, agent.goal)
                moves[new_pos] = d

        if(agent.pos[0] > 0):
            new_pos = tuple(np.subtract(agent.pos, (1, 0)))
            if(self.cells[new_pos[0]][new_pos[1]] == -1 and not(new_pos in next_moves)):
                d = dist(new_pos, agent.goal)
                moves[new_pos] = d

        if(len(moves) == 0):
            return agent.pos
        else:
            dmin = self.grid_size*2 + 1
            kmin = (0,0)
            for k in moves.keys():
                if(moves[k] < dmin):
                    dmin = moves[k]
                    kmin = k

            return kmin

    def print_grid(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                print(str(self.cells[i][j]) + " ", end='')
            print()
        print()


class App(customtkinter.CTk):

    WIDTH = 1000
    HEIGHT = 550

    def __init__(self, grid_size, _game: Taquin):
        super().__init__()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.game = _game
        self.cells = self.game.cells
        self.ref = self.game.goals
        self.grid_size = grid_size
        self.history = [copy.deepcopy(self.cells)]
        self.current_step = 0

        self.repeat = False
        self.title("CustomTkinter complex_example.py")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        
        self.frame = customtkinter.CTkFrame(master=self,
                                            corner_radius=5)
        self.frameRef = customtkinter.CTkFrame(master=self,
                                         corner_radius=5)
        self.frameInfo1 = customtkinter.CTkFrame(master=self,
                                         corner_radius=5)
        self.frameInfo2 = customtkinter.CTkFrame(master=self,
                                         corner_radius=5)

        self.frame.grid(row=0, column=0, sticky="nswe")
        self.frameRef.grid(row=0, column=1, sticky="nswe")
        self.frameInfo1.grid(row=1, column=0, columnspan=1, sticky="nswe")
        self.frameInfo2.grid(row=1, column=1, columnspan=1, sticky="nswe")


        self.labels = []
        self.labelsRef= []
        
        

        self.frameInfo1.columnconfigure(0, weight=0)
        self.frameInfo1.rowconfigure(0, weight=0)
        self.frameInfo2.columnconfigure(0, weight=0)
        self.frameInfo2.rowconfigure(0, weight=0)

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if(self.cells[i][j] == -1):
                    text = ""
                else:
                    text = str(self.cells[i][j])
                label = customtkinter.CTkLabel(master=self.frame,
                                               text=text,
                                               text_font=(
                                                   "Roboto Medium", -16),
                                               width=App.WIDTH/self.grid_size,
                                               height=App.HEIGHT/self.grid_size,
                                               fg_color=("gray75", "gray30"))
                self.labels.append(label)
                label.grid(row=i, column=j, padx=5, pady=5)

        
        for i in range(self.grid_size):
            self.frame.columnconfigure(i, weight=1)
            self.frame.rowconfigure(i, weight=1)
        

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if(self.ref[i][j] == -1):
                    text = ""
                else:
                    text = str(self.ref[i][j])
                label = customtkinter.CTkLabel(master=self.frameRef,
                                               text=text,
                                               text_font=(
                                                   "Roboto Medium", -16),
                                               width=App.WIDTH/self.grid_size,
                                               height=App.HEIGHT/self.grid_size,
                                               fg_color=("gray75", "gray50"))
                self.labelsRef.append(label)
                label.grid(row=i, column=j, padx=5, pady=5)

        for i in range(self.grid_size):
            self.frameRef.columnconfigure(i, weight=1)
            self.frameRef.rowconfigure(i, weight=1)

        self.button_nextStep = customtkinter.CTkButton(master=self.frameInfo1,
                                                text="Next step",
                                                fg_color=("gray75", "gray30"),  # <- custom tuple-color
                                                command=self.button_event_nextStep)
        
        self.button_previousStep = customtkinter.CTkButton(master=self.frameInfo1,
                                                text="Previous step",
                                                fg_color=("gray75", "gray30"),  # <- custom tuple-color
                                                command=self.button_event_previousStep)

        self.button_reset = customtkinter.CTkButton(master=self.frameInfo2,
                                                text="Reset",
                                                fg_color=("gray75", "gray30"),  # <- custom tuple-color
                                                command=self.button_event_reset)

        self.button_stop = customtkinter.CTkButton(master=self.frameInfo2,
                                                text="Stop",
                                                fg_color=("gray75", "gray30"),  # <- custom tuple-color
                                                command=self.button_event_stop)

        self.button_run = customtkinter.CTkButton(master=self.frameInfo2,
                                                text="Run",
                                                fg_color=("gray75", "gray30"),  # <- custom tuple-color
                                                command=self.button_event_run)
        
        self.button_previousStep.grid(row=0, column=0, padx=5, pady=5)
        self.button_nextStep.grid(row=0, column=1, padx=5, pady=5)
        self.button_reset.grid(row=0, column=0, padx=5, pady=5)
        self.button_stop.grid(row=0, column=1, padx=5, pady=5)
        self.button_run.grid(row=0, column=2, padx=5, pady=5)
        
    def update(self):
        if(not self.game.hasEnded()):
            self.cells = copy.deepcopy(self.game.nextState()) 
            cells = copy.deepcopy(self.cells)
            self.history.append(cells)

            self.current_step += 1
            color = '#00FFFF'

            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if(self.cells[i][j] == -1):
                        text = ""
                    else:
                        text = str(self.cells[i][j])
                        if(self.game.agents[self.cells[i][j]].done):
                            color = '#00FF00'
                        else:
                            color = '#00FFFF'

                    self.labels[i*self.grid_size + j].config(text=text, fg= color)
            
            # self.game.print_grid()
        if(self.repeat):
            self.frame.after(500, self.update)
    
    def button_event_nextStep(self):
        print(self.game.hasEnded())
        if(not self.game.hasEnded()):
            
            self.cells = copy.deepcopy(self.game.nextState()) 
            cells = copy.deepcopy(self.cells)
            self.history.append(cells)

            self.current_step += 1

            color = '#00FFFF'

            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if(self.cells[i][j] == -1):
                        text = ""
                    else:
                        text = str(self.cells[i][j])
                        if(self.game.agents[self.cells[i][j]].done):
                            color = '#00FF00'
                        else:
                            color = '#00FFFF'

                    self.labels[i*self.grid_size + j].config(text=text, fg= color)

    def button_event_previousStep(self):
        
        if(self.current_step > 1):
            self.current_step -= 1
            self.game.cells = copy.deepcopy(self.history[self.current_step])
            self.cells = copy.deepcopy(self.game.cells)            

            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if(self.cells[i][j] != -1):
                        self.game.agents[self.cells[i][j]].pos = (i,j)
                        if((i,j) != self.game.agents[self.cells[i][j]].goal):
                            self.game.agents[self.cells[i][j]].done = False

            self.history.pop()
            
            color = '#00FFFF'

            for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if(self.cells[i][j] == -1):
                        text = ""
                    else:
                        text = str(self.cells[i][j])
                        if(self.game.agents[self.cells[i][j]].done):
                            color = '#00FF00'
                        else:
                            color = '#00FFFF'

                    self.labels[i*self.grid_size + j].config(text=text, fg= color)

    def button_event_stop(self):
        self.repeat = False

    def button_event_run(self):
        self.repeat = True
        self.update()

    def button_event_reset(self):
        self.repeat = False

        self.game.reset()
        

        self.cells = self.game.cells
        self.ref = self.game.goals
        self.history = [self.cells]
        self.current_step = 0

        color = '#00FFFF'

        for i in range(self.grid_size):
                for j in range(self.grid_size):
                    if(self.cells[i][j] == -1):
                        text = ""
                    else:
                        text = str(self.cells[i][j])
                        if(self.game.agents[self.cells[i][j]].done):
                            color = '#00FF00'
                        else:
                            color = '#00FFFF'
                    self.labels[i*self.grid_size + j].config(text=text, fg= color)

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if(self.ref[i][j] == -1):
                    text = ""
                else:
                    text = str(self.ref[i][j])

                color = "gray75"
                self.labelsRef[i*self.grid_size + j].config(text=text, fg= color)

        
    def on_closing(self, event=0):
        self.destroy()


if __name__ == "__main__":
    grid_size = 5
    taq = Taquin(grid_size, 2)
    app = App(grid_size, taq)
    app.mainloop()
    # taq.print_grid()
    # taq.cells = taq.nextState()
    # taq.print_grid()
