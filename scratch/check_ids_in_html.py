with open('src/static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

ids_to_check = [
    'btnModeWeek3', 'btnModeWeek4', 'btnClearKb',
    'dropZone', 'fileInput', 'chatForm', 'userInput',
    'btnClearChat', 'btnSuggestedQuestions', 'btnCloseSuggested',
    'sidebarChatBtn', 'sidebarWeek12Btn', 'sidebarRunTicket1aBtn',
    'sidebarRunTicket1bBtn', 'btnRunWeek12Ticket1a', 'btnRunWeek12Ticket1b'
]

for elem_id in ids_to_check:
    print(f"#{elem_id}: {'FOUND' if f'id=\"{elem_id}\"' in html else 'MISSING'}")

