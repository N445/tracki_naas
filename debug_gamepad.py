import pygame, time

pygame.init()
pygame.joystick.init()

count = pygame.joystick.get_count()
if count == 0:
    print("Aucune manette détectée.")
    exit()

joy = pygame.joystick.Joystick(0)
joy.init()

print(f"Nom de la manette : {joy.get_name()}")
print(f"Nombre d'axes     : {joy.get_numaxes()}")
print(f"Nombre de boutons : {joy.get_numbuttons()}")
print(f"Nombre de hats    : {joy.get_numhats()}")

running = True
while running:
    pygame.event.pump()

    # Lire axes
    for i in range(joy.get_numaxes()):
        val = joy.get_axis(i)
        if abs(val) > 0.1:
            print(f"Axis {i} => {val:.2f}")

    # Lire le hat
    for h in range(joy.get_numhats()):
        hat_x, hat_y = joy.get_hat(h)
        # On affiche si != (0,0)
        if (hat_x, hat_y) != (0, 0):
            print(f"Hat {h} => x={hat_x}, y={hat_y}")

    # Bouton B (index 1) pour quitter
    if joy.get_button(1):
        running = False
        print("Bye")

    time.sleep(0.2)

pygame.quit()
