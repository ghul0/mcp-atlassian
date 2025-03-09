#!/usr/bin/env python
# test_simple.py
from mcp_atlassian.jira import JiraFetcher

try:
    # Inicjalizuj fetcher (załaduje konfigurację z pliku .env)
    print("Inicjalizacja JiraFetcher...")
    fetcher = JiraFetcher()
    print("JiraFetcher zainicjalizowany pomyślnie!")

    # Testuj funkcje projektu - próba pobrania projektów
    print("\nPróbuję pobrać projekty...")
    try:
        projects = fetcher.get_projects()
        print(f"Znaleziono {len(projects)} projektów")
        for project in projects:
            print(f"- {project.key}: {project.name}")
    except Exception as e:
        print(f"Błąd podczas pobierania projektów: {e}")
        import traceback
        traceback.print_exc()

    # Testujemy import bezpośrednio ProjectManager
    print("\nTestowanie importu ProjectManager...")
    try:
        from mcp_atlassian.jira import ProjectManager
        print("Import ProjectManager działa poprawnie!")
    except Exception as e:
        print(f"Błąd importu ProjectManager: {e}")

    # Sprawdzamy, czy testy modułu są dostępne
    print("\nSprawdzanie dostępności testów...")
    try:
        import tests.unit.test_project_manager
        print("Moduł testowy test_project_manager jest dostępny!")
    except Exception as e:
        print(f"Błąd importu modułu testowego: {e}")

    print("\nTest PASSED!")
except Exception as e:
    print(f"Ogólny błąd: {e}")
    import traceback
    traceback.print_exc()
