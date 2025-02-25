#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_TITLE_LENGTH 50
#define MAX_AUTHOR_LENGTH 50

/*
    Testdatei: test_porting.c

    Dieses Beispielprogramm verwaltet eine Liste von Büchern im Speicher.
    Jedes Buch hat einen Titel, einen Autor und eine Anzahl von Seiten.
    Es wird dynamischer Speicher für eine wachsende Liste von Büchern verwendet.
    Abschließend kann die Liste sortiert werden und auf dem Bildschirm ausgegeben werden.

    Kompilierung (Beispiel):
    gcc test_porting.c -o test_porting

    Ausführung:
    ./test_porting
*/

typedef struct {
    char title[MAX_TITLE_LENGTH];
    char author[MAX_AUTHOR_LENGTH];
    int pages;
} Book;

void printMenu() {
    printf("------- Buchverwaltung -------\n");
    printf("1) Neues Buch anlegen\n");
    printf("2) Bücher nach Seitenzahl sortieren\n");
    printf("3) Bücher auflisten\n");
    printf("4) Beenden\n");
    printf("--------------------------------\n");
    printf("Auswahl: ");
}

Book createBook() {
    Book newBook;
    printf("Titel des Buches: ");
    // Eingabe bis zum Zeilenende (fgets liest inkl. Zeilenumbruch)
    fgets(newBook.title, MAX_TITLE_LENGTH, stdin);
    // Entferne mögliches Newline
    newBook.title[strcspn(newBook.title, "\n")] = '\0';

    printf("Autor: ");
    fgets(newBook.author, MAX_AUTHOR_LENGTH, stdin);
    newBook.author[strcspn(newBook.author, "\n")] = '\0';

    printf("Seitenanzahl: ");
    scanf("%d", &newBook.pages);

    // Leere Eingabepuffer nach scanf
    getchar();
    return newBook;
}

void sortBooksByPages(Book* books, int count) {
    // Einfacher Bubble-Sort nach Seitenanzahl
    for(int i = 0; i < count - 1; i++) {
        for(int j = 0; j < count - i - 1; j++) {
            if(books[j].pages > books[j+1].pages) {
                Book temp = books[j];
                books[j] = books[j+1];
                books[j+1] = temp;
            }
        }
    }
    printf("Die Bücher wurden nach Seitenzahl sortiert.\n");
}

void printAllBooks(Book* books, int count) {
    if(count == 0) {
        printf("Keine Bücher vorhanden.\n");
        return;
    }
    printf("---- Aktuelle Büchersammlung ----\n");
    for(int i = 0; i < count; i++) {
        printf("%d) \"%s\" von %s (%d Seiten)\n",
               i+1,
               books[i].title,
               books[i].author,
               books[i].pages);
    }
    printf("---------------------------------\n");
}

int main() {
    Book* books = NULL;   // Dynamisches Array
    int capacity = 0;     // Aktuell zugewiesener Speicher (Anzahl Bücher)
    int count = 0;        // Aktuelle Anzahl angelegter Bücher

    while(1) {
        printMenu();
        int choice;
        scanf("%d", &choice);
        getchar(); // Eingabepuffer leeren

        switch(choice) {
            case 1: {
                if(count == capacity) {
                    // Speicher erweitern
                    capacity = (capacity == 0) ? 2 : capacity * 2;
                    books = (Book*)realloc(books, capacity * sizeof(Book));
                    if(!books) {
                        printf("Fehler: Kein Speicher verfügbar.\n");
                        return 1;
                    }
                }
                Book newBook = createBook();
                books[count] = newBook;
                count++;
                break;
            }
            case 2:
                if(count > 1) {
                    sortBooksByPages(books, count);
                } else {
                    printf("Zu wenige Bücher zum Sortieren.\n");
                }
                break;
            case 3:
                printAllBooks(books, count);
                break;
            case 4:
                printf("Beende das Programm.\n");
                free(books);
                return 0;
            default:
                printf("Ungültige Auswahl.\n");
        }
    }
    return 0;
}
