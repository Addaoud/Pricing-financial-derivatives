import numpy as np
import math
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import ttk
import pandas as pd
import seaborn as sns
sns.set()

in_dd=pd.read_csv('EURUSDwithIR.csv')
df_bt=pd.DataFrame(in_dd,columns=['Close','ExREuro','ExRUsd'])


L=pd.date_range(start='1/1/2010', end='1/09/2020')
df2=pd.Series(L.values).to_frame('DATE')



def forward (T,frequency,Time_set,IRx,IRy,S,P,montant,position):
    IRx=IRx*0.01
    IRy=IRy*0.01
    P=P*0.0001
    if (Time_set=="discrete"):
        if (frequency=="quarterly"):
            m=4
            nbp=T//(360/m)
            njr=T%(360/m)
            F=S*((1+IRx/m)/(1+IRy/m))**(nbp)*(1+njr*IRx/360)/(1+njr*IRy/360)
        elif (frequency=="semi-annual"):
            m=2
            nbp=T//(360/m)
            njr=T%(360/m)
            F=S*(((1+IRx/m)/(1+IRy/m))**(nbp))*((1+njr*IRx/360)/(1+njr*IRy/360))
        elif (frequency=="monthly"):
            m=12
            nbp=T//(360/m)
            njr=T%(360/m)
            F=S*((1+IRx/m)/(1+IRy/m))**(nbp)*(1+njr*IRx/360)/(1+njr*IRy/360)
        elif (frequency=="daily"):
            m=360
            nbp=T//(360/m)
            njr=T%(360/m)
            F=S*((1+IRx/m)/(1+IRy/m))**(nbp)*(1+njr*IRx/360)/(1+njr*IRy/360)
        else :
            m=1
            nbp=T//(360/m)
            njr=T%(360/m)
            F=S*((1+IRx/m)/(1+IRy/m))**(nbp)*(1+njr*IRx/360)/(1+njr*IRy/360)
    else : F=S*math.exp((IRx-IRy)*T/360)
    if (position=="Buyer"):
        F=F+P
    else : F=F-P
    M1=F*montant
    return (F,M1)   

    
def plotting(marge):
    df_bt['forward'],df_bt['amount']=forward (180,"monthly","discrete",df_bt['ExREuro'],df_bt['ExRUsd'],df_bt['Close'],marge,10000,"acheteur")
    L1=df_bt['forward'].values.tolist()
    K=[]
    for i in range (len(L1)):
        K.append(i)
    M1=df_bt['Close'].values.tolist()
    plt.plot(K, M1, 'b',label="Spot")
    plt.plot(K, L1, 'r',label="Forward")
    plt.xlabel("Date")
    plt.ylabel("ExR")
    plt.legend()
    plt.show()

def inverse(T,frequency,Time_set,IRx,IRy,S,montant,F,choix):
    P=0
    F1,F2=forward (T,frequency,Time_set,IRx,IRy,S,P,montant,choix[3])
    if (choix[3]=="Buyer"):
        if (F1-F<0):
            while (abs(F1-F)>10**(-4)):
                P+=1
                F1,F2=forward (T,frequency,Time_set,IRx,IRy,S,P,montant,choix[3])
                if (F1-F>0):
                    break ;
        elif (F1-F==0):
            P=0
        else:
            while (abs(F1-F)>10**(-4)):
                S-=int(choix[0])*0.0001
                IRx-=int(choix[1])*0.0001*IRx
                IRy+=int(choix[2])*0.0001*IRx
                F1,F2=forward (T,frequency,Time_set,IRx,IRy,S,P,montant,choix[3])
                if (F1-F<0):
                    break;
    else :
        if (F1-F>0):
            while (abs(F1-F)>10**(-4)):
                P+=1
                F1,F2=forward (T,frequency,Time_set,IRx,IRy,S,P,montant,choix[3])
                if (F1-F<0):
                    break ;
        elif (F1-F==0):
            P=0
        else:
            while (abs(F1-F)>10**(-4)):
                S+=int(choix[0])*0.0001
                IRx+=int(choix[1])*0.0001*IRx
                IRy-=int(choix[2])*0.0001*IRx
                F1,F2=forward (T,frequency,Time_set,IRx,IRy,S,P,montant,choix[3])
                if (F1-F>0):
                    break;
    return (P,S,IRx,IRy)


def swap(T,T1,frequency,Time_set,IRx,IRy,IRx1,IRy1,S):
    IRx=IRx*0.01
    IRy=IRy*0.01
    IRx1=IRx1*0.01
    IRy1=IRy1*0.01
    P=0
    position="Buyer"
    if (T==0):
        F=S
    else:
        F=forward (T,frequency,Time_set,IRx,IRy,S,P,1000,position)[0]
    F1=forward (T1,frequency,Time_set,IRx1,IRy1,S,P,1000,position)[0]
    ps=(F1-F)*1000
    return (ps)


def accrued_coupons(df,VN,freq,emission_date,current_date,c): #coupon is annual interest rate.
    f=0
    emission_date=pd.to_datetime(emission_date)
    current_date=pd.to_datetime(current_date)
    last_pay_date=emission_date
    if freq=='Q':
        f=30*3
    elif freq=='S':
        f=30*6
    elif freq=='A':
        f=30*12
    while(df.loc[df['DATE']==current_date].index[0]>=df.loc[df['DATE']==last_pay_date].index[0] + f):
        index=df.loc[df['DATE']==last_pay_date].index[0]
        index+=f
        last_pay_date=df.iloc[index]['DATE']
   
    number_of_days=df.loc[df['DATE']==current_date].index[0]-df.loc[df['DATE']==last_pay_date].index[0]
    acc_coupon=(c*0.01*VN*number_of_days)/(360)
    return round(acc_coupon,4)

def gross_price(df,VN,VR,freq,current_date,maturity_date,emission_date,c,YTM): #YTM and C are annual rates.
    L=[]
    f=0
    emission_date=pd.to_datetime(emission_date)
    maturity_date=pd.to_datetime(maturity_date)
    current_date=pd.to_datetime(current_date)
    last_pay_date=emission_date
    n_periods=0
    c=c*0.01
    YTM=YTM*0.01
    
    
    if freq=='Q':
        f=30*3 #frequency in days
        n_periods=4 #number of coupon payments per year
    elif freq=='S':
        f=30*6  #frequency in days
        n_periods=2 #number of coupon payments per year
    elif freq=='A':
        f=30*12 #frequency in days
        n_periods=1 #number of coupon payments per year
        
    while(df.loc[df['DATE']==current_date].index[0]>=df.loc[df['DATE']==last_pay_date].index[0] + f): #while udpated date + frequency do not surpass the current date
        index=df.loc[df['DATE']==last_pay_date].index[0]
        index+=f
        last_pay_date=df.iloc[index]['DATE'] #last coupon yield date
    
    date_of_next_pay=df.iloc[df.loc[df['DATE']==last_pay_date].index[0]+f]['DATE'] #date of next coupon yield
    days_to_maturity=df.loc[df['DATE']==maturity_date].index[0]-df.loc[df['DATE']==current_date].index[0] #days until maturity
    number_of_payments=days_to_maturity//f #Number of received payments until maturity
    days_to_next_coupon=days_to_maturity%f #Number of remaining days until next coupon yield.
    L.append(VN*c/((1+YTM/n_periods)**(days_to_next_coupon*n_periods/360)))
    i=1
    while(i<number_of_payments):
             L.append(VN*c/((1+YTM)**(i+n_periods*days_to_next_coupon/360)))
             i+=1
    L.append(VR/((1+YTM)**(i+n_periods*days_to_next_coupon/360)))
    if (YTM==c):
        return (VR)
    return round(sum(L),4)


def clean_price(df,VN,VR,c,freq,emission_date,maturity_date,current_date, YTM):
    acc_coupons=accrued_coupons(df=df,VN=VN,freq=freq,current_date=current_date,emission_date=emission_date,c=c)
    gross_p=gross_price(df=df,VN=VN,VR=VR,freq=freq,current_date=current_date,maturity_date=maturity_date,emission_date=emission_date,c=c,YTM=YTM)
    return round(gross_p-acc_coupons,4)

def dichotomy(YTM1,YTM2,tol,max_iter,df,VN,VR,c,freq,emission_date,maturity_date,current_date, P): #YTM1<YTM2 Please :D
    P_mid=0
    P1=0
    P2=0
    counter=0
    YTM=0
    P1=gross_price(df=df,VN=VN,VR=VR,freq=freq,current_date=current_date,maturity_date=maturity_date,emission_date=emission_date,c=c,YTM=YTM1)
    P2=gross_price(df=df,VN=VN,VR=VR,freq=freq,current_date=current_date,maturity_date=maturity_date,emission_date=emission_date,c=c,YTM=YTM2)
    while( (counter<max_iter) & ( abs(YTM2-YTM1)/YTM1>tol ) ):
        
        YTM=(YTM1+YTM2)/2
        P_mid=gross_price(df=df,VN=VN,VR=VR,freq=freq,current_date=current_date,maturity_date=maturity_date,emission_date=emission_date,c=c,YTM=YTM)
        
        if ( (P1 < P) & (P_mid < P) )  :
            YTM1=YTM
        elif ( (P1 > P) & (P_mid > P) ):
            YTM1=YTM
        else:
            YTM2=YTM
            
        counter+=1
    return round(YTM,4)

def duration(df,VN,VR,c,freq,current_date,maturity_date,emission_date,YTM): #Durations is returned in years.
    L=[]
    f=0
    x=0
    emission_date=pd.to_datetime(emission_date)
    maturity_date=pd.to_datetime(maturity_date)
    current_date=pd.to_datetime(current_date)
    last_pay_date=emission_date
    n_periods=0
    P=gross_price(df=df,VN=VN,VR=VR,freq=freq,current_date=current_date,maturity_date=maturity_date,emission_date=emission_date,c=c,YTM=YTM)
    c=c*0.01
    YTM=YTM*0.01
    
    
    if freq=='Q':
        f=30*3 #frequency in days
        n_periods=4 #number of coupon payments per year
    elif freq=='S':
        f=30*6  #frequency in days
        n_periods=2 #number of coupon payments per year
    elif freq=='A':
        f=30*12 #frequency in days
        n_periods=1 #number of coupon payments per year
        
    while(df.loc[df['DATE']==current_date].index[0]>=df.loc[df['DATE']==last_pay_date].index[0] + f): #while udpated date + frequency do not surpass the current date
        index=df.loc[df['DATE']==last_pay_date].index[0]
        index+=f
        last_pay_date=df.iloc[index]['DATE'] #last coupon yield date
    
    date_of_next_pay=df.iloc[df.loc[df['DATE']==last_pay_date].index[0]+f]['DATE'] #date of next coupon yield
    days_to_maturity=df.loc[df['DATE']==maturity_date].index[0]-df.loc[df['DATE']==current_date].index[0] #days until maturity
    number_of_payments=days_to_maturity//f #Number of received payments until maturity
    days_to_next_coupon=days_to_maturity%f #Number of remaining days until next coupon yield.
    L.append(VN*c/((1+YTM/n_periods)**(days_to_next_coupon*n_periods/360)))
    i=1
    while(i<number_of_payments):
        x=(VN*c/((1+YTM)**(i+n_periods*days_to_next_coupon/360)))
        x=x*(i+1)
        L.append(x)
        i+=1
    x=(VR/((1+YTM)**(i+n_periods*days_to_next_coupon/360)))
    x=number_of_payments*x
    L.append(x)
    
    return round((sum(L)/P)/n_periods,4)

def action1():
    marge=100
    plotting(marge)

def action ():
    entryTE.delete(0,END)
    entryM.delete(0,END)
    montant= float (entrymontant.get())
    choix=str (listecombom.get())
    frequency=str (listecombo.get())
    Time_set=str(listecombo1.get())
    IRx=float (entryIRx.get())
    IRy=float (entryIRy.get())
    S=float (entryS.get())
    if (choix=="margin in pips"):
        P=int (entryP.get())
    else :
        P=(float(entryP.get())/montant)*10000
        P=int (P//1)
    T=int (entryT.get())
    position=str (listecombop.get())
    F,M1=forward(T,frequency,Time_set,IRx,IRy,S,P,montant,position)
    F=round(F,4)
    M1=round(M1,3)
    entryTE.insert(0,F)
    entryM.insert(0,M1)

def action2 ():
    entrymarge1.delete(0,END)
    entryS1.delete(0,END)
    entryIRx1.delete(0,END)
    entryIRy1.delete(0,END)
    entrymnt1.delete(0,END)
    montant=float (entrymontant.get())
    frequency=str (listecombo.get())
    Time_set=str(listecombo1.get())
    IRx=float (entryIRx.get())
    IRy=float (entryIRy.get())
    S=float (entryS.get())
    P=int (entryP.get())
    T=int (entryT.get())
    F=float (entryForward.get())
    h=montant*F
    choix=[]
    v1=c1.get()
    choix.append(v1)
    v2=c2.get()
    choix.append(v2)
    v3=c3.get()
    choix.append(v3)
    position=str (listecombop1.get())
    choix.append(position)
    P1,S1,IRx1,IRy1=inverse(T,frequency,Time_set,IRx,IRy,S,montant,F,choix)
    entrymarge1.insert(0,P1)
    entryS1.insert(0,S1)
    entryIRx1.insert(0,IRx1)
    entryIRy1.insert(0,IRy1)
    entrymnt1.insert(0,h)

def action3 ():
    entrydif.delete(0,END)
    entrydif1.delete(0,END)
    S1=float (entrySpotbid.get())
    S2=float (entrySpotask.get())
    mat1=int(entrymat1.get())
    mat2=int(entrymat2.get())
    IRxT1=float(entryIRxT1.get())
    IRxT11=float(entryIRxT11.get())
    IRxT2=float(entryIRxT2.get())
    IRxT21=float(entryIRxT21.get())
    IRyT1=float(entryIRyT1.get())
    IRyT11=float(entryIRyT11.get())
    IRyT2=float(entryIRyT2.get())
    IRyT21=float(entryIRyT21.get())
    S=(S1+S2)/2
    frequency=str (listecombofq.get())
    Time_set=str(listecombost.get())
    sp=swap(mat1,mat2,frequency,Time_set,IRxT11,IRyT1,IRxT2,IRyT21,S)*1000
    sp1=swap(mat1,mat2,frequency,Time_set,IRxT1,IRyT11,IRxT21,IRyT2,S)*1000
    sp=int(sp//1)
    sp1=int(sp1//1)
    entrydif.insert(0,sp)
    entrydif1.insert(0,sp1)

def action4():
    entryYP.delete(0,END)
    entryDUR.delete(0,END)
    entrySEN.delete(0,END)
    entrycpcc.delete(0,END)
    entrycpcc1.delete(0,END)
    freq=str(entryfrq.get())
    emission_date=str(entryED.get())
    current_date=str(entryCD.get())
    maturity_date=str(entryMD.get())
    VN=int(entryVN.get())
    VR=int(entryVR.get())
    c=float(entryCP.get())
    x=str (listbonds.get())
    o=float(entryYTM.get())
    df=df2
    if (x=="Yield to maturity"):
        lblYP.configure(text="Bond price")
        bp=gross_price(df,VN,VR,freq,current_date,maturity_date,emission_date,c,o)
        clean=clean_price(df,VN,VR,c,freq,emission_date,maturity_date,current_date, o)
        coupon_couru=accrued_coupons(df,VN,freq,emission_date,current_date,c)
        entrycpcc.insert(0,clean)
        entrycpcc1.insert(0,coupon_couru)
        dur=duration(df,VN,VR,c,freq,current_date,maturity_date,emission_date,o)
        sen=round(dur/(1+o*0.01),4)
        entryYP.insert(0,bp)
        entryDUR.insert(0,dur)
        entrySEN.insert(0,sen)
        
    else:
        lblYP.configure(text="Yield to maturity")
        ytm=dichotomy(0.1,100,10**-6,10**8,df,VN,VR,c,freq,emission_date,maturity_date,current_date, o)
        clean=clean_price(df,VN,VR,c,freq,emission_date,maturity_date,current_date, ytm)
        coupon_couru=accrued_coupons(df,VN,freq,emission_date,current_date,c)
        entrycpcc.insert(0,clean)
        entrycpcc1.insert(0,coupon_couru)
        dur=duration(df,VN,VR,c,freq,current_date,maturity_date,emission_date,ytm)
        sen=round(dur/(1+ytm*0.01),4)
        entryYP.insert(0,ytm)
        entryDUR.insert(0,dur)
        entrySEN.insert(0,sen)
    
    

    
fen=Tk()
fen.geometry("1600x1600")
C = Canvas(fen, bg="blue", height=1600, width=1600)
filename = PhotoImage(file = "AP.png")
background_label = Label(fen, image=filename)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

C.pack()


lblmontant=Label(fen,text="Amount in local change")
lblmontant.place(x=50,y=200)
entrymontant=Entry(fen)
entrymontant.place(x=250,y=200)

lblfrequency=Label(fen,text="Frenquency")
lblfrequency.place(x=50,y=100)
listefrq=["monthly","annual","quarterly","daily","semi-annual"]
listecombo=ttk.Combobox(fen, values=listefrq)
listecombo.pack()
listecombo.place(x=250,y=100)


lblTime_set=Label(fen,text="Set time")
lblTime_set.place(x=50,y=50)
listetime=["discrete","continuous"]
listecombo1=ttk.Combobox(fen, values=listetime)
listecombo1.pack()
listecombo1.place(x=250,y=50)



lblIRx=Label(fen,text="Local interest rate")
lblIRx.place(x=50,y=300)
entryIRx=Entry(fen)
entryIRx.place(x=250,y=300)

lblIRy=Label(fen,text="Foreign interest rate")
lblIRy.place(x=50,y=350)
entryIRy=Entry(fen)
entryIRy.place(x=250,y=350)

lblS=Label(fen,text="Spot Exchange rate")
lblS.place(x=50,y=250)
entryS=Entry(fen)
entryS.place(x=250,y=250)

listemarge=["margin in pips","margin in amount"]
listecombom=ttk.Combobox(fen, values=listemarge)
listecombom.pack()
listecombom.place(x=50,y=400)
entryP=Entry(fen)
entryP.place(x=250,y=400)


lblT=Label(fen,text="Maturity in days")
lblT.place(x=50,y=150)
entryT=Entry(fen)
entryT.place(x=250,y=150)

lblfd=Label(fen,text="Pricing of Forward")
lblfd.place(x=150,y=450)

lblPos=Label(fen,text="Position")
lblPos.place(x=50,y=500)
listepos=["Buyer","Seller"]
listecombop=ttk.Combobox(fen, values=listepos)
listecombop.pack()
listecombop.place(x=150,y=500)
Submit=Button (fen, text="Submit",command=action)
Submit.place (x=300,y=500)


Backtest=Button (fen, text="BackTesting",command=action1)
Backtest.place (x=150,y=650)

lblTE=Label(fen,text="Forward Exchange rate")
lblTE.place(x=50,y=550)
entryTE=Entry(fen)
entryTE.place(x=250,y=550)

lblM=Label(fen,text="Forward amount")
lblM.place(x=50,y=600)
entryM=Entry(fen)
entryM.place(x=250,y=600)

Simuler=Button (fen, text="Simulate",command=action2)
Simuler.place (x=550,y=200)


lblPos1=Label(fen,text="Position")
lblPos1.place(x=400,y=50)
listepos1=["Buyer","Seller"]
listecombop1=ttk.Combobox(fen, values=listepos1)
listecombop1.pack()
listecombop1.place(x=550,y=50)
lblForward=Label(fen,text="enter the forward")
lblForward.place(x=400,y=100)
entryForward=Entry(fen)
entryForward.place(x=550,y=100)

c1=IntVar()
case=Checkbutton(fen,text="spot?",variable=c1)
case.pack()
case.place(x=450,y=150)
c2=IntVar()
case1=Checkbutton(fen,text="LIR?",variable=c2)
case1.pack()
case1.place(x=550,y=150)
c3=IntVar()
case2=Checkbutton(fen,text="FIR?",variable=c3)
case2.pack()
case2.place(x=650,y=150)

lblS1=Label(fen,text="Adjusted Spot")
lblS1.place(x=400,y=250)
entryS1=Entry(fen)
entryS1.place(x=550,y=250)
lblIRx1=Label(fen,text="Adjusted LIR")
lblIRx1.place(x=400,y=300)
entryIRx1=Entry(fen)
entryIRx1.place(x=550,y=300)
lblIRy1=Label(fen,text="Adjusted FIR")
lblIRy1.place(x=400,y=350)
entryIRy1=Entry(fen)
entryIRy1.place(x=550,y=350)
lblmarge1=Label(fen,text="margin")
lblmarge1.place(x=400,y=400)
entrymarge1=Entry(fen)
entrymarge1.place(x=550,y=400)
lblmnt1=Label(fen,text="Forward amount")
lblmnt1.place(x=400,y=450)
entrymnt1=Entry(fen)
entrymnt1.place(x=550,y=450)

lblSwap=Label(fen,text="Swaps")
lblSwap.place(x=880,y=50)
lblSpotbid=Label(fen,text="Spot bid")
lblSpotbid.place(x=750,y=100)
entrySpotbid=Entry(fen,width=10)
entrySpotbid.place(x=900,y=100)
lblSpotask=Label(fen,text="Spot ask")
lblSpotask.place(x=750,y=150)
entrySpotask=Entry(fen,width=10)
entrySpotask.place(x=900,y=150)
lblmat1=Label(fen,text="1st maturity in days")
lblmat1.place(x=750,y=200)
entrymat1=Entry(fen)
entrymat1.place(x=900,y=200)
lblmat2=Label(fen,text="2nd maturity in days")
lblmat2.place(x=750,y=250)
entrymat2=Entry(fen)
entrymat2.place(x=900,y=250)
lblIRxT1=Label(fen,text="Local IR at T1  bid-ask")
lblIRxT1.place(x=750,y=300)
entryIRxT1=Entry(fen,width=10)
entryIRxT1.place(x=900,y=300)
entryIRxT11=Entry(fen,width=10)
entryIRxT11.place(x=960,y=300)
lblIRxT2=Label(fen,text="Local IR at T2 bid-ask")
lblIRxT2.place(x=750,y=350)
entryIRxT2=Entry(fen,width=10)
entryIRxT2.place(x=900,y=350)
entryIRxT21=Entry(fen,width=10)
entryIRxT21.place(x=960,y=350)
lblIRyT1=Label(fen,text="Foreign IR at T1 bid-ask")
lblIRyT1.place(x=750,y=400)
entryIRyT1=Entry(fen,width=10)
entryIRyT1.place(x=900,y=400)
entryIRyT11=Entry(fen,width=10)
entryIRyT11.place(x=960,y=400)
lblIRyT2=Label(fen,text="Foreign IR at T2 bid-ask")
lblIRyT2.place(x=750,y=450)
entryIRyT2=Entry(fen,width=10)
entryIRyT2.place(x=900,y=450)
entryIRyT21=Entry(fen,width=10)
entryIRyT21.place(x=960,y=450)
lblfrequency1=Label(fen,text="Frequency")
lblfrequency1.place(x=750,y=550)
listecombofq=ttk.Combobox(fen, values=listefrq)
listecombofq.pack()
listecombofq.place(x=900,y=550)
lblTime_set1=Label(fen,text="Set time")
lblTime_set1.place(x=750,y=500)
listecombost=ttk.Combobox(fen, values=listetime)
listecombost.pack()
listecombost.place(x=900,y=500)
Submit1=Button (fen, text="Submit",command=action3)
Submit1.place (x=880,y=600)
lbldif=Label(fen,text="Swap points")
lbldif.place(x=750,y=650)
entrydif=Entry(fen,width=10)
entrydif.place(x=900,y=650)
entrydif1=Entry(fen,width=10)
entrydif1.place(x=960,y=650)


lblbond=Label(fen,text="Bonds")
lblbond.place(x=1180,y=10)
lblVN=Label(fen,text="Face value")
lblVN.place(x=1050,y=100)
entryVN=Entry(fen)
entryVN.place(x=1200,y=100)
lblVR=Label(fen,text="Redemption value")
lblVR.place(x=1050,y=150)
entryVR=Entry(fen)
entryVR.place(x=1200,y=150)
lblED=Label(fen,text="Emission date")
lblED.place(x=1050,y=200)
entryED=Entry(fen)
entryED.place(x=1200,y=200)
lblCD=Label(fen,text="Present date")
lblCD.place(x=1050,y=250)
entryCD=Entry(fen)
entryCD.place(x=1200,y=250)
lblMD=Label(fen,text="Maturity date")
lblMD.place(x=1050,y=300)
entryMD=Entry(fen)
entryMD.place(x=1200,y=300)
lblCP=Label(fen,text="Annuel coupon rate")
lblCP.place(x=1050,y=350)
entryCP=Entry(fen)
entryCP.place(x=1200,y=350)
listebond=["Yield to maturity","Bond price"]
listbonds=ttk.Combobox(fen, values=listebond)
listbonds.pack()
listbonds.place(x=1050,y=400)
entryYTM=Entry(fen)
entryYTM.place(x=1200,y=400)
lblfrq=Label(fen,text="Frequency")
lblfrq.place(x=1050,y=50)
listefrq=["Q","S","A"]
entryfrq=ttk.Combobox(fen, values=listefrq)
entryfrq.pack()
entryfrq.place(x=1200,y=50)
Submitbonds=Button (fen, text="Submit",command=action4)
Submitbonds.place (x=1150,y=450)
lblYP=Label(fen,text="Yield to maturity")
lblYP.place(x=1050,y=500)
entryYP=Entry(fen)
entryYP.place(x=1200,y=500)
lblDUR=Label(fen,text="Duration in years")
lblDUR.place(x=1050,y=600)
entryDUR=Entry(fen)
entryDUR.place(x=1200,y=600)
lblcpcc=Label(fen,text="Clean price/Accrued couppon")
lblcpcc.place(x=1050,y=550)
entrycpcc=Entry(fen,width=10)
entrycpcc.place(x=1200,y=550)
entrycpcc1=Entry(fen,width=10)
entrycpcc1.place(x=1260,y=550)
lblSEN=Label(fen,text="Sensibility in %")
lblSEN.place(x=1050,y=650)
entrySEN=Entry(fen)
entrySEN.place(x=1200,y=650)

fen.mainloop()
