#coding: utf-8

from tkinter import*


login = Tk()
login.title("My application")
login.geometry("500x300")
login.config(background="gray30")

def connexion():

    couleur = {"nero": "#252726", "purple": "#800080", "white": "#FFFFFF"}
    N_fenetre = Toplevel()
    N_fenetre.title("Bienvenu")
    N_fenetre.geometry("500x300")  # Ajusté pour une taille cohérente
    N_fenetre.config(bg="gray30")
    
    
    topFrame = Frame(N_fenetre, bg="#800080")
    topFrame.pack(side="top", fill=X)

    
    info = Label(N_fenetre, text = "Nous disposons des produits à vos gouts", font=100, bg="gray30",  fg="#FFFFFF")
    info.pack(expand=True)
               

frame = Frame(master = login, bg ="#252726" )
frame.pack(pady= 20, padx= 90, fill = "both", expand= True)

label = Label(master = frame , text= "se connecter", bg="#252726", font= "#FFFFFF",fg="#FFFFFF")
label.pack(pady = 12, padx = 10)


champ1 = Entry(master = frame, text = " identifiant")
champ1.pack(pady=12)

champ2 = Entry(master = frame, text = " mot de pass", show= "*" )
champ2.pack(pady=15)

champ3 = Entry(master = frame, text = " confirmer mot de pass", show= "*")
champ3.pack(pady=15)

button = Button(master = frame, text= "connexion", command=connexion, bg ="#800080" )
button.pack(pady=12,padx=10)

#checkbox = CheckBox(master = frame, text =" se souvenir de moi")

login.mainloop()