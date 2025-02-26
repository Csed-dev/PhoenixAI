def berechneunddruckeDaten(a,b,c):
 summe=a+b+c
 produkt=a*b*c
 durchschnitt=summe/3
 if summe>100:
    print("Summe ist größer als 100")
 else:
    print("Summe ist 100 oder weniger")
 print("Summe:",summe,"Produkt:",produkt,"Durchschnitt:",durchschnitt)
 for i in range(a):
    for j in range(b):
        print(i,j)
 for k in range(c):
    print("Index:",k)
 print("Fertig mit Schleifen")

def verarbeiteListe(liste):
 ergebnis=[]
 for item in liste:
    if item%2==0:
        ergebnis.append(item*2)
    else:
        ergebnis.append(item+1)
 for item in ergebnis:
    if item>10:
        print("Großer Wert:",item)
 return ergebnis

def leseDateiUndSchreibeAusgabe(eingabeDatei,ausgabeDatei):
 try:
    f=open(eingabeDatei,'r')
    inhalt=f.read()
    f.close()
    daten=[int(x) for x in inhalt.split()]
    verarbeiteterInhalt=verarbeiteListe(daten)
    f=open(ausgabeDatei,'w')
    for num in verarbeiteterInhalt:
        f.write(str(num)+"\n")
    f.close()
 except Exception as e:
    print("Ein Fehler ist aufgetreten:",e)

def berechneMatrix(matrix):
 ergebnisse=[]
 for i in range(len(matrix)):
    for j in range(len(matrix[i])):
        ergebnisse.append(matrix[i][j]*2)
        if matrix[i][j]>50:
            print("Hoher Wert in Matrix:",matrix[i][j])
 return ergebnisse

def generiereZahlenUndBerechne(liste):
 result=[]
 for num in liste:
    if num<0:
        result.append(abs(num))
    else:
        result.append(num*3)
 for res in result:
    print("Verarbeitet:",res)
 return result

def leseEingabe():
 print("Geben Sie Zahlen ein, getrennt durch Leerzeichen:")
 eingabe=input()
 daten=[int(x) for x in eingabe.split()]
 return daten

def speichereDaten(daten,dateiname):
 try:
    f=open(dateiname,'w')
    for item in daten:
        f.write(str(item)+"\n")
    f.close()
    print("Daten gespeichert in",dateiname)
 except Exception as e:
    print("Fehler beim Speichern:",e)

def main():
 daten=[1,2,3,4,5,6,7,8,9,10]
 ergebnis=verarbeiteListe(daten)
 berechneunddruckeDaten(10,20,30)
 leseDateiUndSchreibeAusgabe('eingabe.txt','ausgabe.txt')
 matrix=[[1,2,3],[4,5,6],[7,8,9]]
 matrixErgebnis=berechneMatrix(matrix)
 eingabe=leseEingabe()
 generierteZahlen=generiereZahlenUndBerechne(eingabe)
 speichereDaten(generierteZahlen,'output.txt')
 for nummer in ergebnis:
    print(nummer)

if __name__=="__main__":
 main()