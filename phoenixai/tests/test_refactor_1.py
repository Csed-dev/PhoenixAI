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
def verarbeiteListe(liste):
 ergebnis=[]
 for item in liste:
    if item%2==0:
        ergebnis.append(item*2)
    else:
        ergebnis.append(item+1)
 return ergebnis
def leseDateiUndSchreibeAusgabe(eingabeDatei,ausgabeDatei):
 try:
    f=open(eingabeDatei,'r')
    inhalt=f.read()
    f.close()
    verarbeiteterInhalt=verarbeiteListe([int(x) for x in inhalt.split()])
    f=open(ausgabeDatei,'w')
    for num in verarbeiteterInhalt:
        f.write(str(num)+"\n")
    f.close()
 except Exception as e:
    print("Ein Fehler ist aufgetreten:",e)
def main():
 daten=[1,2,3,4,5,6,7,8,9,10]
 ergebnis=verarbeiteListe(daten)
 berechneunddruckeDaten(10,20,30)
 leseDateiUndSchreibeAusgabe('eingabe.txt','ausgabe.txt')
 for nummer in ergebnis:
    print(nummer)
if __name__=="__main__":
 main()
