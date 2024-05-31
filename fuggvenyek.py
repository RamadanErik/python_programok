"""------------------FÜGGVÉNYEK-----------------------"""
import csv
import numpy as np
import matplotlib
from pathlib import Path
import matplotlib.pyplot as plt
import time
import clr
import sys
import logging
from datetime import datetime
import os
from mpl_toolkits.mplot3d import Axes3D

logger = logging.getLogger(__name__)

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.PolarizerCLI.dll")
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.PolarizerCLI import *
from System import Decimal

sys.path.append("C:\\Users\\KNL2022\\Documents\\TimeController_V1_10_0\\Examples\\Python")
from utils.common import zmq_exec
from utils.common import connect
from utils.acquisitions import (
    setup_input_counts_over_time_acquisition
)

def save_rand_counts_to_csv(fokok2,adatok3,optimum,opt_ertek,idokezdet,probalkozasok_szama):
    filepath="C:\\Users\\KNL2022\\PycharmProjects\\Poincare\\csvk\\meres_rand.csv"
    with open(filepath, 'a', newline="") as csvfile:
        writer_object = csv.writer(csvfile, delimiter=";")
        writer_object.writerow(["Start"])
        for i in range(len(fokok2)):
            lista = []
            for k in range(len(fokok2[0])):
                lista.append(fokok2[i][k])
            for detektor in range(4):
                lista.append(adatok3[i][detektor])
            writer_object.writerow(lista)
            print(lista)

        csvfile.close()
    filepath = "C:\\Users\\KNL2022\\PycharmProjects\\Poincare\\csvk\\optimum_rand.csv"
    with open(filepath, 'a', newline="") as csvfile:
        writer_object = csv.writer(csvfile, delimiter=";")
        lista=[probalkozasok_szama]
        ts = time.time()
        ido = datetime.fromtimestamp(ts)

        for i in range(len(optimum)):
            lista.append(int(optimum[i]))
        for i in range(len(opt_ertek)):
            lista.append(int(opt_ertek[i]))
        lista.append([ido.year,ido.month,ido.day,ido.hour,ido.minute,ido.second,ido.microsecond])
        idovege = datetime.now()
        lista.append(idovege - idokezdet)
        writer_object.writerow(lista)
        csvfile.close()

    return


def save_counts_to_csv(fokok2,adatok3,optimum,opt_ertek,idokezdet):
    filepath="C:\\Users\\KNL2022\\PycharmProjects\\Poincare\\csvk\\meres.csv"
    with open(filepath, 'a', newline="") as csvfile:
        writer_object = csv.writer(csvfile, delimiter=";")
        writer_object.writerow(["Start"])
        for i in range(len(fokok2)): #2
            seged_tomb = [0, 0, 0]
            for k in range(len(fokok2[0])):  # 3
                for j in range(len(fokok2[0][0][0])): #10
                    lista=[]
                    for paddle in range(3):
                        lista.append(int(fokok2[i][paddle][0][(seged_tomb[paddle])]))
                    seged_tomb[k]+=1
                    if seged_tomb[k]>=len(fokok2[0][0][0]):
                        seged_tomb[k]-=1
                    for detektor in range(4):
                        lista.append(adatok3[i][k][j][detektor])
                    writer_object.writerow(lista)
                    print(lista)

        csvfile.close()
    filepath = "C:\\Users\\KNL2022\\PycharmProjects\\Poincare\\csvk\\optimum.csv"
    with open(filepath, 'a', newline="") as csvfile:
        writer_object = csv.writer(csvfile, delimiter=";")
        lista=[]
        ts = time.time()
        ido = datetime.fromtimestamp(ts)

        for i in range(len(optimum)):
            lista.append(int(optimum[i]))
        for i in range(len(opt_ertek)):
            lista.append(int(opt_ertek[i]))
        lista.append([ido.year,ido.month,ido.day,ido.hour,ido.minute,ido.second,ido.microsecond])
        idovege = datetime.now()
        lista.append(idovege - idokezdet)
        writer_object.writerow(lista)
        csvfile.close()

    return

def save_grad_counts_to_csv(fokok2,adatok3,optimum,opt_ertek,idokezdet,learning_rate,eltolas):
    filepath="C:\\Users\\KNL2022\\PycharmProjects\\Poincare\\csvk\\meres_grad.csv"
    with open(filepath, 'a', newline="") as csvfile:
        writer_object = csv.writer(csvfile, delimiter=";")
        writer_object.writerow(["Start","Learningrate",learning_rate,"Eltolas",eltolas])
        for i in range(len(fokok2)):
            lista = []
            for k in range(len(fokok2[0])):
                lista.append(fokok2[i][k])
            lista.append(adatok3[i])
            writer_object.writerow(lista)
            print(lista)

        csvfile.close()
    filepath = "C:\\Users\\KNL2022\\PycharmProjects\\Poincare\\csvk\\optimum_grad.csv"
    with open(filepath, 'a', newline="") as csvfile:
        writer_object = csv.writer(csvfile, delimiter=";")
        lista=[]
        ts = time.time()
        ido = datetime.fromtimestamp(ts)

        for i in range(len(optimum)):
            lista.append(int(optimum[i]))
        lista.append(int(opt_ertek))
        lista.append([ido.year,ido.month,ido.day,ido.hour,ido.minute,ido.second,ido.microsecond])
        idovege = datetime.now()
        lista.append(idovege - idokezdet)
        writer_object.writerow(lista)
        csvfile.close()

    return
def optimum_kereso(device,tc,paddle,min,max,db):
    adatok=[]

    probalk=[]
    adat_elso=0
    maxérték = 0
    opt=0

    for i in np.linspace(min, max, db):
        d = Decimal(i)
        device.MoveTo(d, paddle, 60000)
        lista=[]
        for j in range(1,5):
            adat2 = zmq_exec(tc, f"INPUt{j}:COUNter?")
            adat = int(adat2)
            if(j==1):
                adat_elso=adat
            lista.append(adat)
        adatok.append(lista)
        probalk.append(i)
        print(f"Fok:{round(i,2)} Mérés:{lista[0]}")
        time.sleep(0.2)
        if adat_elso > maxérték:
            maxérték = adat_elso
            opt = i

    d = Decimal(opt)
    device.MoveTo(d, paddle, 60000)
    print(f'OPTIMUM: {round(opt,2)}')

    return [probalk,adatok,opt]

def optimum_kereso2(device,tc,paddle,min,max,db,melyikre_opt):
    adatok=[]

    probalk=[]
    adat_elso=0
    maxérték = 0
    opt=0

    for i in np.linspace(min, max, db):
        d = Decimal(i)
        device.MoveTo(d, paddle, 60000)
        lista=[]
        for j in range(1,5):
            adat2 = zmq_exec(tc, f"INPUt{j}:COUNter?")
            adat = int(adat2)
            if(j==melyikre_opt+1):
                adat_elso=adat
            lista.append(adat)
        adatok.append(lista)
        probalk.append(i)
        print(f"Fok:{round(i,2)} Mérés:{lista[0]}")
        time.sleep(0.2)
        if adat_elso > maxérték:
            maxérték = adat_elso
            opt = i

    d = Decimal(opt)
    device.MoveTo(d, paddle, 60000)
    print(f'OPTIMUM: {round(opt,2)}')

    return [probalk,adatok,opt]


def beallit3(device,paddles,poz):
    d = Decimal(int(poz[0]))
    device.MoveTo(d, paddles[0], 60000)
    d = Decimal(int(poz[1]))
    device.MoveTo(d, paddles[1], 60000)
    d = Decimal(int(poz[2]))
    device.MoveTo(d, paddles[2], 60000)
    time.sleep(0.5)
    return



def parcialis_derivaltak(device,tc,paddles,poz,eltolas):
    parc=[0,0,0]
    for i in range(3):
        ertek = int(zmq_exec(tc, f"INPUt{1}:COUNter?"))
        time.sleep(0.5)
        if poz[i] < (170-eltolas):
            d=Decimal(int(poz[i]+eltolas))
            n=1
        else:
            d=Decimal(int(poz[i]-eltolas))
            n=-1
        print(f"Mozgatás{d},{paddles[i]}")
        device.MoveTo(d,paddles[i],60000)

        ertek2 = int(zmq_exec(tc, f"INPUt{1}:COUNter?"))
        time.sleep(0.5)
        parc[i] = int((ertek2-ertek)*n*(1/eltolas))
        d = Decimal(poz[i])
        device.MoveTo(d, paddles[i], 60000)


    return parc


def kompatibilis_fokok(fokok):
    for i in range(3):
        if fokok[i]<0:
            fokok[i]=0
        elif fokok[i]>170:
            fokok[i]=170

    return fokok
def kereso_algoritmus_gradiens(device,tc,paddle1,paddle2,paddle3,db,kezdopoz):
    adatok = []
    probalk = []
    learning_rate=0.01
    eltolas=5
    poz = kezdopoz
    paddles = [paddle1, paddle2, paddle3]

    'Kezdőpozíció beállítás'
    beallit3(device,paddles,poz)

    ujpoz=[0,0,0]
    for hanyszor in range(db):

        'Parciális derváltak'
        parc=parcialis_derivaltak(device,tc,paddles,poz,10)
        print(f"Parciális deriváltak:{parc[0]},{parc[1]},{parc[2]}")
        for i in range(3):
            valtozas=parc[i]*learning_rate
            if valtozas>60:
                valtozas=60
            elif valtozas<-60:
                valtozas=-60
            ujpoz[i]=poz[i]-valtozas

        ujpoz=kompatibilis_fokok(ujpoz)
        poz=ujpoz


        print(f"Új fokok: {round(poz[0],2)},{round(poz[1],2)},{round(poz[2],2)}")
        ertek = int(zmq_exec(tc, f"INPUt{1}:COUNter?"))

        adatok.append(ertek)
        print(f"Mérés: {round(ertek,2)}")
        time.sleep(0.5)
        beallit3(device,paddles,ujpoz)
        probalk.append([poz[0],poz[1],poz[2]])
    opt=ujpoz

    return [probalk,adatok,opt,ertek,learning_rate,eltolas]

def uj_min(a,mennyivel): #kell majd#
    c=a-mennyivel
    if(c<0):
        c=0
    return c

def uj_max(a,mennyivel): #kell majd#
    c=a+mennyivel
    if(c>170):
        c=170
    return c


def kontrollerhez_csatlakozas():
    try:
        serial_no = str("38290024")
        DeviceManagerCLI.BuildDeviceList()
        device = Polarizer.CreatePolarizer(serial_no)
        print(DeviceManagerCLI.GetDeviceList())

        # Connect, begin polling, and enable
        print("Connecting to MPC320")
        device.Connect(serial_no)

        time.sleep(0.25)
        device.StartPolling(250)
        time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device

        device.EnableDevice()
        time.sleep(0.25)  # Wait for device to enable

        # Get Device information
        device_info = device.GetDeviceInfo()
        print(device_info.Description)

        paddle11 = PolarizerPaddles.Paddle1
        paddle22 = PolarizerPaddles.Paddle2
        paddle33 = PolarizerPaddles.Paddle3

        # Wait for Settings to Initialise
        if not device.IsSettingsInitialized():
            device.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert device.IsSettingsInitialized() is True
    except Exception as e:
        print(e)
        #sys.exit(1)
    return device, paddle11, paddle22, paddle33

def kontrollerhez_csatlakozas2(serial_no):
    try:
        serial_no = str(serial_no)
        DeviceManagerCLI.BuildDeviceList()
        device = Polarizer.CreatePolarizer(serial_no)
        print(DeviceManagerCLI.GetDeviceList())

        # Connect, begin polling, and enable
        print("Connecting to MPC320")
        device.Connect(serial_no)

        time.sleep(0.25)
        device.StartPolling(250)
        time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device

        device.EnableDevice()
        time.sleep(0.25)  # Wait for device to enable

        # Get Device information
        device_info = device.GetDeviceInfo()
        print(device_info.Description)

        paddle11 = PolarizerPaddles.Paddle1
        paddle22 = PolarizerPaddles.Paddle2
        paddle33 = PolarizerPaddles.Paddle3

        # Wait for Settings to Initialise
        if not device.IsSettingsInitialized():
            device.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert device.IsSettingsInitialized() is True
    except Exception as e:
        print(e)
        #sys.exit(1)
    return device, paddle11, paddle22, paddle33

def time_controller_csatlakozas():
    try:
        # Default Time Controller IP address
        DEFAULT_TC_ADDRESS = "169.254.104.112"

        # Default number of counter acquisitions
        DEFAULT_NUMBER_OF_ACQUISITIONS = 5

        # Default file path where counts are saved in CSV format (None = do not save)
        DEFAULT_COUNTS_FILEPATH = "input_counts.csv"

        # Default counter integration time ps
        mp = 0.5  # Másodpercben az integration time
        DEFAULT_COUNTERS_INTEGRATION_TIME = int(mp * (10 ^ 12))

        # Default list of input counts to acquire
        DEFAULT_COUNTERS = ["1", "2", "3", "4"]

        # Default log file path where logging output is stored
        DEFAULT_LOG_PATH = None

        tc = connect(DEFAULT_TC_ADDRESS)
        hist_to_counter_map, actual_integration_time = setup_input_counts_over_time_acquisition(
            tc, DEFAULT_COUNTERS_INTEGRATION_TIME, DEFAULT_COUNTERS
        )
    except AssertionError as e:
        logger.error(e)
        sys.exit(1)

    except ConnectionError as e:
        logger.exception(e)
        sys.exit(1)
    return tc


def figure3d(fokok_rand,adatok,i2):
    fokok_rand=np.array(fokok_rand)
    adatok=np.array(adatok)
    # Make data
    x = np.array(fokok_rand[:, 0])
    y = np.array(fokok_rand[:, 1])
    z = np.array(fokok_rand[:, 2])

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

    colors = adatok[:, 0]
    ertekek = adatok[:, 0]

    colors = colors / max(colors)

    colormap = plt.cm.ScalarMappable(cmap='seismic')
    nagysag=150*10/i2
    ax.scatter(x, y, z, c=colormap.to_rgba(colors), s=nagysag,marker='d')

    ax.set_xlim(0, 170)
    ax.set_ylim(0, 170)
    ax.set_zlim(0, 170)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    ax.set_xticks([0, 85, 170])
    ax.set_yticks([0, 85, 170])
    ax.set_zticks([0, 85, 170])

    ax.set_xticklabels(['0', '85', '170'])
    ax.set_yticklabels(['0', '85', '170'])
    ax.set_zticklabels(['0', '85', '170'])

    # Add color bar
    cbar = fig.colorbar(colormap, ax=ax, orientation='vertical', shrink=0.8, aspect=10)
    cbar.set_label('Színskála')
    cbar.set_ticks([min(colors), max(colors)])
    cbar.set_ticklabels([f'{min(ertekek):.0f}', f'{max(ertekek):.0f}'])

    # Create a new directory with the current timestamp
    current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    directory_path = f"C:/Users/KNL2022/PycharmProjects/Poincare/képek/figures_rand_{current_time}"
    os.makedirs(directory_path)
    # Save figure in the created directory
    fig_name = f"{directory_path}/figurerand.png"
    plt.savefig(fig_name)
    plt.draw()
    plt.close(fig)
    return

def kereso_algoritmus_sima(device,tc,iteraciok_szama,db):
    optimum = [0, 0, 0]
    paddle1 = PolarizerPaddles.Paddle1
    paddle2 = PolarizerPaddles.Paddle2
    paddle3 = PolarizerPaddles.Paddle3
    min = [0, 0, 0]
    max = [170, 170, 170]

    # 'töröld kell hozzá opt input'
    # for i in range(3):
    #     min[i] = uj_min(opt[i], 20)
    #     max[i] = uj_max(opt[i], 20)
    '  '
    fokok_ki=[]
    adatok_ki=[]

    # Create a new directory with the current timestamp
    current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    directory_path = f"C:/Users/KNL2022/PycharmProjects/Poincare/képek/figures_{current_time}"
    os.makedirs(directory_path)

    for j in range(iteraciok_szama):
        fokok_ki.append([[],[],[]])
    for j in range(iteraciok_szama):
        fokok = []
        adatok2 = []
        probalk, adatok, optimum[0] = optimum_kereso(device, tc, paddle1, min[0], max[0], db)
        fokok.append(probalk)
        fokok_ki[j][0].append(probalk)
        adatok2.append(adatok)
        probalk, adatok, optimum[1] = optimum_kereso(device, tc, paddle2, min[1], max[1], db)
        fokok.append(probalk)
        fokok_ki[j][1].append(probalk)
        adatok2.append(adatok)
        probalk, adatok, optimum[2] = optimum_kereso(device, tc, paddle3, min[2], max[2], db)
        fokok.append(probalk)
        fokok_ki[j][2].append(probalk)
        adatok2.append(adatok)
        adatok3 = np.array(adatok2)
        adatok_ki.append(adatok3)
        for c in range(4):
            #figure3d(fokok[0],fokok[1],fokok[2],adatok[:,:,c])
            fig = plt.figure(j * 4 + c + 2)
            for v in range(3):
                plt.plot(fokok[v], adatok3[:, :, c][v],label=f'{v + 1}. tárcsa')
            plt.xlim(0, 170)
            fig.suptitle(f'{c + 1}. detektor')
            plt.legend(loc='lower left')
            # Save figure in the created directory
            fig_name = f"{directory_path}/figure_{j}_{c + 1}.png"
            plt.savefig(fig_name)
            plt.draw()
            plt.close(fig)

        for i in range(3):
            min[i] = uj_min(optimum[i], 20/(j+1))
            max[i] = uj_max(optimum[i], 20/(j+1))
    return fokok_ki,adatok_ki,optimum

def kereso_algoritmus_sima2(device,tc,iteraciok_szama,db,melyikre_opt):
    optimum = [0, 0, 0]
    paddle1 = PolarizerPaddles.Paddle1
    paddle2 = PolarizerPaddles.Paddle2
    paddle3 = PolarizerPaddles.Paddle3
    min = [0, 0, 0]
    max = [170, 170, 170]

    # 'töröld kell hozzá opt input'
    # for i in range(3):
    #     min[i] = uj_min(opt[i], 20)
    #     max[i] = uj_max(opt[i], 20)
    '  '
    fokok_ki=[]
    adatok_ki=[]

    # Create a new directory with the current timestamp
    current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    directory_path = f"C:/Users/KNL2022/PycharmProjects/Poincare/képek/figures_{current_time}"
    os.makedirs(directory_path)

    for j in range(iteraciok_szama):
        fokok_ki.append([[],[],[]])
    for j in range(iteraciok_szama):
        fokok = []
        adatok2 = []
        probalk, adatok, optimum[0] = optimum_kereso2(device, tc, paddle1, min[0], max[0], db, melyikre_opt)
        fokok.append(probalk)
        fokok_ki[j][0].append(probalk)
        adatok2.append(adatok)
        probalk, adatok, optimum[1] = optimum_kereso2(device, tc, paddle2, min[1], max[1], db, melyikre_opt)
        fokok.append(probalk)
        fokok_ki[j][1].append(probalk)
        adatok2.append(adatok)
        probalk, adatok, optimum[2] = optimum_kereso2(device, tc, paddle3, min[2], max[2], db, melyikre_opt)
        fokok.append(probalk)
        fokok_ki[j][2].append(probalk)
        adatok2.append(adatok)
        adatok3 = np.array(adatok2)
        adatok_ki.append(adatok3)

        for i in range(3):
            min[i] = uj_min(optimum[i], 20/(j+1))
            max[i] = uj_max(optimum[i], 20/(j+1))
    return fokok_ki,adatok_ki,optimum

def optimum_kereso3(device,tc,paddle,min,max,db,melyikre_opt,utolso): #EZ MÉG ITT NEM JÓ rosszra optimalizál sztem, beütés kéne nem koincidencia


    adatok=[]

    probalk=[]
    adat=0
    maxérték = 0
    opt=0

    for i in np.linspace(min, max, db):
        d = Decimal(i)
        device.MoveTo(d, paddle, 60000)
        lista=[]
        adat = utolso[melyikre_opt]
        print(f"Fok:{round(i,2)} Mérés:{adat}")
        time.sleep(0.2)
        if adat > maxérték:
            maxérték = adat
            opt = i

    d = Decimal(opt)
    device.MoveTo(d, paddle, 60000)
    print(f'OPTIMUM: {round(opt,2)}')

    return [probalk,adatok,opt]
def kereso_algoritmus_sima3(device,tc,iteraciok_szama,db,melyikre_opt,utolso):

    optimum = [0, 0, 0]
    paddle1 = PolarizerPaddles.Paddle1
    paddle2 = PolarizerPaddles.Paddle2
    paddle3 = PolarizerPaddles.Paddle3
    min = [0, 0, 0]
    max = [170, 170, 170]

    fokok_ki=[]
    adatok_ki=[]

    for j in range(iteraciok_szama):
        fokok_ki.append([[],[],[]])
    for j in range(iteraciok_szama):
        fokok = []
        adatok2 = []
        probalk, adatok, optimum[0] = optimum_kereso3(device, tc, paddle1, min[0], max[0], db, melyikre_opt,utolso)
        fokok.append(probalk)
        fokok_ki[j][0].append(probalk)
        adatok2.append(adatok)
        probalk, adatok, optimum[1] = optimum_kereso3(device, tc, paddle2, min[1], max[1], db, melyikre_opt,utolso)
        fokok.append(probalk)
        fokok_ki[j][1].append(probalk)
        adatok2.append(adatok)
        probalk, adatok, optimum[2] = optimum_kereso3(device, tc, paddle3, min[2], max[2], db, melyikre_opt,utolso)
        fokok.append(probalk)
        fokok_ki[j][2].append(probalk)
        adatok2.append(adatok)
        adatok3 = np.array(adatok2)
        adatok_ki.append(adatok3)

        for i in range(3):
            min[i] = uj_min(optimum[i], 20/(j+1))
            max[i] = uj_max(optimum[i], 20/(j+1))
    return fokok_ki,adatok_ki,optimum


def kereso_algoritmus_random(device,tc,hatar,probalkozasi_limit,paddle1,paddle2,paddle3):
    beallitott_fokok = []  # új
    kapcs = -1
    minimum_fokok = -1
    #------------------
    maximum_beutes=[0,0,0,0]
    #------------------
    pontok=10

    adatok_ki=[]

    x = []
    y = []
    z = []
    i2 = 1

    while maximum_beutes[0] < hatar and i2<probalkozasi_limit:
        fokok = np.random.rand(pontok, 3) * 170
        for i in range(pontok):
            fok1 = int(fokok[i, 0])
            fok2 = int(fokok[i, 1])
            fok3 = int(fokok[i, 2])

            beallitott_fokok.append([fok1, fok2, fok3])
            d1 = Decimal(fok1)
            d2 = Decimal(fok2)
            d3 = Decimal(fok3)

            device.MoveTo(d1, paddle1, 60000)
            device.MoveTo(d2, paddle2, 60000)
            device.MoveTo(d3, paddle3, 60000)

            time.sleep(0.1)
            adat_tomb=[]
            for j in range(1, 5):
                adat2 = zmq_exec(tc, f"INPUt{j}:COUNter?")
                adat = int(adat2)
                if (j == 1):
                    adat_elso = adat
                adat_tomb.append(adat)
            adatok_ki.append(adat_tomb)

            print(f"{i2}. vizsgálat: {fok1},{fok2},{fok3} fokoknál a beütések száma: {adat_elso}")
            i2 += 1  # Hanyadik vizsgálat
            if (adat_elso>maximum_beutes[0] or kapcs == -1):
                kapcs = 1
                maximum_beutes=adat_tomb
                minimum_fokok = fokok[i]

            if (maximum_beutes[0]>hatar):
                break
    figure3d(beallitott_fokok, adatok_ki,i2)
    return beallitott_fokok,adatok_ki,minimum_fokok,maximum_beutes,i2