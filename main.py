INSTRUMENTS = {
    "1": {"name": "Piano / Flute / Gitar (C)", "value": 0},
    "2": {"name": "Soprano Sax/ Tenor Sax / Trompet (Bb)", "value": 2},
    "3": {"name": "Alto Sax/ Bariton Sax (Eb)", "value": 9},
    "4": {"name": "Korno (F)", "value": 7}
}

def find_note_index(note):
    # Map that changes sharps and flats to numbers.
    note_map = {
        'C': 0,  'B#': 0, 'C#': 1, 'DB': 1, 'D': 2, 'D#': 3, 'EB': 3,
        'E': 4,  'FB': 4, 'F': 5,  'E#': 5, 'F#': 6, 'GB': 6, 'G': 7,
        'G#': 8, 'AB': 8, 'A': 9, 'A#': 10, 'BB': 10, 'B': 11, 'CB': 11
    }
    return note_map.get(note.upper().strip(), -1)

def transposer(note_data, source_value, target_value):
    rem_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # 1. Check and separate the beat
    if ":" in note_data:
        parts = note_data.split(":")
        clean_note = parts[0]
        beat_suffix = ":" + parts[1]
    else:
        clean_note = note_data
        beat_suffix = " "

    # 2. Find index of the clean note
    current_index = find_note_index(clean_note)

    # invalid logs
    if current_index == -1: return note_data

    remaining = target_value - source_value

    new_index = (current_index + remaining) % 12
    
    # Return the new note WITH the beat suffix
    return rem_notes[new_index] + beat_suffix

def instrument_select(question_text):
    print(f"\n{question_text}")
    for key, val in INSTRUMENTS.items():
        print(f"{key}. {val['name']}")

    while True:
        choice = input("Choose: ")
        if choice in INSTRUMENTS:
            return INSTRUMENTS[choice]
        print("Wrong choice please try again.")

if __name__ == "__main__":
    print("\n🎵 NOTE TRANSPOSER 🎵")
    print("---------------------------")

    source_info = instrument_select("Which instrument does the note belong to?")
    target_info = instrument_select("Which instrument do you want to adapt this sheet music for?")

    print("-" * 40)
    print(f"MOD: {source_info['name']} --> {target_info['name']}")
    print("Format example: C:4 or D#:0,5 .")
    print("For exit press q.")
    print("-" * 40)
    
    while True:
        input_notes = input("\nEnter the notes: ")
        if input_notes.lower() == 'q':
            break
            
        raw_notes = input_notes.split()
        new_notes = []
        
        for n in raw_notes:
            # Fonksiyona artık sayısal değerleri gönderiyoruz
            sonuc = transposer(n, source_info['value'], target_info['value'])
            new_notes.append(sonuc)
            
        print(f"👉 Transposed: {' '.join(new_notes)}")

