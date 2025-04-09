import psycopg2
import bcrypt
from tkinter import *
from tkinter import messagebox, ttk

# URL de la base de données
DATABASE_URL = "postgresql://neondb_owner:QvVHIdpc2y0w@ep-lively-hat-a27dkpf4.eu-central-1.aws.neon.tech/neondb?sslmode=require"

# Variable globale pour stocker le user_id
current_user_id = None

# Fonction pour centrer une fenêtre
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

# Fonction de connexion
def ouvrir_connexion():
    fenetre_connexion = Toplevel(window)
    fenetre_connexion.title("Connexion")
    fenetre_connexion.config(bg="black")
    center_window(fenetre_connexion, 400, 300)

    Label(fenetre_connexion, text="Connexion", font=("Courrier", 20), fg="white", bg="black").pack(pady=10)

    Label(fenetre_connexion, text="Email :", font=("Courrier", 14), fg="white", bg="black").pack()
    email_entry = Entry(fenetre_connexion, font=("Courrier", 14))
    email_entry.pack(pady=5)

    Label(fenetre_connexion, text="Mot de passe :", font=("Courrier", 14), fg="white", bg="black").pack()
    mdp_entry = Entry(fenetre_connexion, font=("Courrier", 14), show="*")
    mdp_entry.pack(pady=5)

    def verifier_connexion():
        global current_user_id  # Utiliser la variable globale
        email = email_entry.get()
        mdp = mdp_entry.get()
        try:
            # Connexion à la base de données
            connection = psycopg2.connect(DATABASE_URL)
            cursor = connection.cursor()

            # Récupérer le hash du mot de passe et l'ID de l'utilisateur
            cursor.execute("SELECT user_id, password FROM \"user\" WHERE email = %s;", (email,))
            result = cursor.fetchone()

            if result:
                user_id, hashed_password = result

                # Vérifier le mot de passe avec bcrypt
                if bcrypt.checkpw(mdp.encode('utf-8'), hashed_password.encode('utf-8')):
                    # Stocker le user_id dans la variable globale
                    current_user_id = user_id

                    # Afficher un message de succès
                    success_label = Label(fenetre_connexion, text="Connexion réussie !", font=("Courrier", 14), fg="green", bg="black")
                    success_label.pack(pady=10)

                    # Fermer la fenêtre de connexion et ouvrir une nouvelle page après 1 seconde
                    fenetre_connexion.after(1000, lambda: (fenetre_connexion.destroy(), window.destroy(), ouvrir_nouvelle_page()))
                else:
                    messagebox.showerror("Erreur", "Mot de passe incorrect.")
            else:
                messagebox.showerror("Erreur", "Email non trouvé.")

            # Fermer le curseur et la connexion
            cursor.close()
            connection.close()

        except psycopg2.DatabaseError as db_err:
            messagebox.showerror("Erreur de base de données", f"Erreur de connexion à la base de données : {db_err}")
        except Exception as error:
            messagebox.showerror("Erreur", f"Erreur inattendue : {error}")

    Button(fenetre_connexion, text="Valider", font=("Courrier", 14), command=verifier_connexion).pack(pady=20)

def ouvrir_nouvelle_page():
    nouvelle_fenetre = Tk()
    nouvelle_fenetre.title("Menu")
    nouvelle_fenetre.attributes("-fullscreen", True)
    nouvelle_fenetre.config(bg="black")

    Label(nouvelle_fenetre, text="INVENTORY", fg="white", font=("Courrier", 24), bg="black").place(relx=0.0, rely=0.1)

    # Bouton Quitter
    Button(nouvelle_fenetre, text="Quitter", bg="red", fg="white", font=("Courrier", 20), command=nouvelle_fenetre.quit).place(relx=0.9, rely=0.1)

    # Bouton Inventaire
    Button(nouvelle_fenetre, text="Inventaire", bg="black", fg="white", font=("Courrier", 20), command=lambda: afficher_inventaire(nouvelle_fenetre)).place(relx=0.25, rely=0.1)

    # Bouton Achats
    Button(nouvelle_fenetre, text="Achats", bg="black", fg="white", font=("Courrier", 20), command=lambda: afficher_achats(nouvelle_fenetre)).place(relx=0.37, rely=0.1)

    # Bouton Ventes
    Button(nouvelle_fenetre, text="Ventes", bg="black", fg="white", font=("Courrier", 20), command=lambda: afficher_ventes(nouvelle_fenetre)).place(relx=0.47, rely=0.1)

    # Bouton Statistiques
    Button(nouvelle_fenetre, text="Statistiques", bg="black", fg="white", font=("Courrier", 20), command=lambda: afficher_statistiques(nouvelle_fenetre)).place(relx=0.57, rely=0.1)

    # Bouton Profile
    Button(nouvelle_fenetre, text="Profile", bg="black", fg="white", font=("Courrier", 20), command=lambda: afficher_profile(nouvelle_fenetre)).place(relx=0.71, rely=0.1)

    nouvelle_fenetre.mainloop()

def afficher_inventaire(fenetre):
    # Effacer le contenu précédent sous les boutons
    for widget in fenetre.winfo_children():
        if widget.winfo_y() > 100:  # Supprimer uniquement les widgets en dessous des boutons
            widget.destroy()

    Label(fenetre, text="Inventaire", font=("Courrier", 20), fg="white", bg="black").pack(pady=(150, 10))

    # Créer un widget Treeview pour afficher l'inventaire sous forme de tableau
    style = ttk.Style()
    style.configure("Treeview", background="black", foreground="white", fieldbackground="black", rowheight=25)
    style.map('Treeview', background=[('selected', 'gray')], foreground=[('selected', 'white')])

    tree = ttk.Treeview(fenetre, columns=("ID", "Nom", "Quantité", "Prix"), show="headings", style="Treeview")
    tree.heading("ID", text="ID")
    tree.heading("Nom", text="Nom")
    tree.heading("Quantité", text="Quantité")
    tree.heading("Prix", text="Prix")
    tree.pack(pady=20)

    try:
        # Connexion à la base de données
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()

        # Récupérer les données d'inventaire
        cursor.execute("SELECT product_id, name, stock_quantity, price FROM product;")
        inventaire = cursor.fetchall()

        # Insérer les données dans le Treeview
        for produit in inventaire:
            tree.insert("", "end", values=(produit[0], produit[1], produit[2], produit[3]))

        # Fermer le curseur et la connexion
        cursor.close()
        connection.close()

    except psycopg2.DatabaseError as db_err:
        messagebox.showerror("Erreur de base de données", f"Erreur de connexion à la base de données : {db_err}")
    except Exception as error:
        messagebox.showerror("Erreur", f"Erreur inattendue : {error}")

def afficher_achats(fenetre):
    # Effacer le contenu précédent sous les boutons
    for widget in fenetre.winfo_children():
        if widget.winfo_y() > 100:  # Supprimer uniquement les widgets en dessous des boutons
            widget.destroy()

    Label(fenetre, text="Achats", font=("Courrier", 20), fg="white", bg="black").pack(pady=(150, 10))

    # Champ pour entrer le nom du produit
    Label(fenetre, text="Nom du produit :", font=("Courrier", 14), fg="white", bg="black").pack()
    nom_entry = Entry(fenetre, font=("Courrier", 14))
    nom_entry.pack(pady=5)

    # Champ pour entrer le prix
    Label(fenetre, text="Prix :", font=("Courrier", 14), fg="white", bg="black").pack()
    prix_entry = Entry(fenetre, font=("Courrier", 14))
    prix_entry.pack(pady=5)

    # Champ pour entrer la quantité
    Label(fenetre, text="Quantité :", font=("Courrier", 14), fg="white", bg="black").pack()
    quantite_entry = Entry(fenetre, font=("Courrier", 14))
    quantite_entry.pack(pady=5)

    def effectuer_achat():
        nom = nom_entry.get()
        prix = prix_entry.get()
        quantite = quantite_entry.get()

        if not nom or not prix or not quantite:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return

        try:
            # Connexion à la base de données
            connection = psycopg2.connect(DATABASE_URL)
            cursor = connection.cursor()

            # Vérifier si le produit existe déjà
            cursor.execute("SELECT product_id FROM product WHERE name = %s;", (nom,))
            existing_product = cursor.fetchone()

            if existing_product:
                # Mettre à jour la quantité et updated_at du produit existant
                cursor.execute("UPDATE product SET stock_quantity = stock_quantity + %s, updated_at = NOW() WHERE product_id = %s RETURNING stock_quantity;",
                               (quantite, existing_product[0]))
                new_quantity = cursor.fetchone()[0]

                # Vérifier si la quantité est zéro et supprimer le produit si nécessaire
                if new_quantity == 0:
                    cursor.execute("DELETE FROM product WHERE product_id = %s;", (existing_product[0],))

            else:
                # Insérer un nouveau produit avec updated_at
                cursor.execute("INSERT INTO product (name, price, stock_quantity, updated_at) VALUES (%s, %s, %s, NOW());",
                               (nom, prix, quantite))

            connection.commit()

            # Fermer le curseur et la connexion
            cursor.close()
            connection.close()

            messagebox.showinfo("Succès", "Achat effectué avec succès !")
            afficher_achats(fenetre)  # Mettre à jour l'affichage des achats

        except psycopg2.DatabaseError as db_err:
            messagebox.showerror("Erreur de base de données", f"Erreur de connexion à la base de données : {db_err}")
        except Exception as error:
            messagebox.showerror("Erreur", f"Erreur inattendue : {error}")

    # Bouton pour effectuer l'achat
    Button(fenetre, text="Acheter", font=("Courrier", 14), command=effectuer_achat).pack(pady=20)

def afficher_ventes(fenetre):
    # Effacer le contenu précédent sous les boutons
    for widget in fenetre.winfo_children():
        if widget.winfo_y() > 100:  # Supprimer uniquement les widgets en dessous des boutons
            widget.destroy()

    Label(fenetre, text="Ventes", font=("Courrier", 20), fg="white", bg="black").pack(pady=(150, 10))

    # Champ pour entrer l'ID du produit
    Label(fenetre, text="ID du produit :", font=("Courrier", 14), fg="white", bg="black").pack()
    product_id_entry = Entry(fenetre, font=("Courrier", 14))
    product_id_entry.pack(pady=5)

    # Champ pour entrer la quantité
    Label(fenetre, text="Quantité :", font=("Courrier", 14), fg="white", bg="black").pack()
    quantite_entry = Entry(fenetre, font=("Courrier", 14))
    quantite_entry.pack(pady=5)

    # Champ pour entrer le prix de vente
    Label(fenetre, text="Prix de vente :", font=("Courrier", 14), fg="white", bg="black").pack()
    prix_vente_entry = Entry(fenetre, font=("Courrier", 14))
    prix_vente_entry.pack(pady=5)

    def enregistrer_vente():
        product_id = product_id_entry.get()
        quantity = quantite_entry.get()
        sales_price = prix_vente_entry.get()

        if not product_id or not quantity or not sales_price:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return

        try:
            # Connexion à la base de données
            connection = psycopg2.connect(DATABASE_URL)
            cursor = connection.cursor()

            # Insérer une nouvelle vente dans la table sale en utilisant le user_id récupéré
            cursor.execute("INSERT INTO sale (user_id, product_id, quantity, sales_price) VALUES (%s, %s, %s, %s);",
                           (current_user_id, product_id, quantity, sales_price))
            connection.commit()

            # Mettre à jour la quantité en stock et updated_at du produit
            cursor.execute("UPDATE product SET stock_quantity = stock_quantity - %s, updated_at = NOW() WHERE product_id = %s RETURNING stock_quantity;",
                           (quantity, product_id))
            new_quantity = cursor.fetchone()[0]

            # Vérifier si la quantité est zéro et supprimer le produit si nécessaire
            if new_quantity == 0:
                cursor.execute("DELETE FROM product WHERE product_id = %s;", (product_id,))

            connection.commit()

            # Fermer le curseur et la connexion
            cursor.close()
            connection.close()

            messagebox.showinfo("Succès", "Vente enregistrée avec succès !")
            afficher_ventes(fenetre)  # Mettre à jour l'affichage des ventes

        except psycopg2.DatabaseError as db_err:
            messagebox.showerror("Erreur de base de données", f"Erreur de connexion à la base de données : {db_err}")
        except Exception as error:
            messagebox.showerror("Erreur", f"Erreur inattendue : {error}")

    # Bouton pour enregistrer la vente
    Button(fenetre, text="Vendre", font=("Courrier", 14), command=enregistrer_vente).pack(pady=20)

def afficher_profile(fenetre):
    # Effacer le contenu précédent sous les boutons
    for widget in fenetre.winfo_children():
        if widget.winfo_y() > 100:  # Supprimer uniquement les widgets en dessous des boutons
            widget.destroy()

    Label(fenetre, text="Profile", font=("Courrier", 20), fg="white", bg="black").pack(pady=(150, 10))

    try:
        # Connexion à la base de données
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()

        # Récupérer les informations de l'utilisateur
        cursor.execute("SELECT pseudo, first_name, last_name, email, birthday, gender FROM \"user\" WHERE user_id = %s;", (current_user_id,))
        user_info = cursor.fetchone()

        # Afficher les informations de l'utilisateur
        if user_info:
            info_text = f"Pseudo: {user_info[0]}\nNom: {user_info[1]} {user_info[2]}\nEmail: {user_info[3]}\nDate de naissance: {user_info[4]}\nGenre: {user_info[5]}"
            Label(fenetre, text=info_text, font=("Courrier", 14), fg="white", bg="black", justify=LEFT).pack(pady=20)

        # Fermer le curseur et la connexion
        cursor.close()
        connection.close()

    except psycopg2.DatabaseError as db_err:
        messagebox.showerror("Erreur de base de données", f"Erreur de connexion à la base de données : {db_err}")
    except Exception as error:
        messagebox.showerror("Erreur", f"Erreur inattendue : {error}")

def afficher_statistiques(fenetre):
    # Effacer le contenu précédent sous les boutons
    for widget in fenetre.winfo_children():
        if widget.winfo_y() > 100:  # Supprimer uniquement les widgets en dessous des boutons
            widget.destroy()

    Label(fenetre, text="Statistiques", font=("Courrier", 20), fg="white", bg="black").pack(pady=(150, 10))

    try:
        # Connexion à la base de données
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()

        # Récupérer le nombre total de produits
        cursor.execute("SELECT COUNT(*) FROM product;")
        total_products = cursor.fetchone()[0]

        # Récupérer le nombre total de ventes
        cursor.execute("SELECT COUNT(*) FROM sale;")
        total_sales = cursor.fetchone()[0]

        # Récupérer la valeur totale des ventes
        cursor.execute("SELECT SUM(sales_price * quantity) FROM sale;")
        total_sales_value = cursor.fetchone()[0]

        # Afficher les statistiques
        stats_text = f"Nombre total de produits: {total_products}\nNombre total de ventes: {total_sales}\nValeur totale des ventes: {total_sales_value} €"
        Label(fenetre, text=stats_text, font=("Courrier", 14), fg="white", bg="black", justify=LEFT).pack(pady=20)

        # Fermer le curseur et la connexion
        cursor.close()
        connection.close()

    except psycopg2.DatabaseError as db_err:
        messagebox.showerror("Erreur de base de données", f"Erreur de connexion à la base de données : {db_err}")
    except Exception as error:
        messagebox.showerror("Erreur", f"Erreur inattendue : {error}")

# Fonction pour quitter l'application
def quitter_application():
    window.quit()

# Fenêtre principale
window = Tk()
window.title("Inventory")
window.attributes("-fullscreen", True)
window.config(bg="black")

titre = Label(window, text="INVENTORY", bg="black", fg="white", font=("Courrier", 40))
titre.place(relx=0.5, rely=0.4, anchor=CENTER)

# Bouton Se connecter
inscription = Button(window, text="Se connecter", bg="black", fg="white", font=("Courrier", 20), command=ouvrir_connexion)
inscription.place(relx=0.5, rely=0.5, anchor=CENTER)

# Bouton Quitter
quitter = Button(window, text="Quitter", bg="red", fg="white", font=("Courrier", 20), command=quitter_application)
quitter.place(relx=0.5, rely=0.6, anchor=CENTER)

window.mainloop()
