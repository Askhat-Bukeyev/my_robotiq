from robotiq_USB import Robotiq_USB
import time
# Create class object
Gr = Robotiq_USB()
print('Activation finished')

Gr.close()
time.sleep(1)
print(Gr.check_object())
print('Current: ',Gr.current)
print('position: ',Gr.position)
time.sleep(1)
Gr.open()

for i in range(3,-1,-1):
    print('Mode: ',i)
    Gr.set_mode(i)
    time.sleep(2)


Gr.move(mode = 0, speed = 250, pos = 200, force = 255)
time.sleep(1)
Gr.move(mode = 0, speed = 100, pos = 0, force = 255)
print('Current: ',Gr.current)


Gr.move_finger([0,150,150,0],[0,100,150,0],[0,255,255,0])
Gr.move_finger([0,0,0,200],[0,0,0,200],[0,0,0,255],scissors = True)

Gr.move(mode = 0, speed = 255, pos = 0, force = 255)
Gr.deactivate()
Gr.exit()