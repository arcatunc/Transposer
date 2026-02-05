import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="🎷 Note Transposer", page_icon="🎵", layout="centered")

INSTRUMENTS = {
    "Piano / Flute / Guitar (C)": 0,
    "Soprano / Tenor Sax / Trumpet (Bb)": 2,
    "Alto Sax / Baritone Sax (Eb)": 9,
    "French Horn (F)": 7
}

def find_note_index(note):
    note_map = {
        'C': 0,  'B#': 0, 'C#': 1, 'DB': 1, 'D': 2, 'D#': 3, 'EB': 3,
        'E': 4,  'FB': 4, 'F': 5,  'E#': 5, 'F#': 6, 'GB': 6, 'G': 7,
        'G#': 8, 'AB': 8, 'A': 9, 'A#': 10, 'BB': 10, 'B': 11, 'CB': 11
    }
    return note_map.get(note.upper().strip(), -1)

def transposer(note_data, source_value, target_value):
    abc_notes_map = ['C', '^C', 'D', '^D', 'E', 'F', '^F', 'G', '^G', 'A', '^A', 'B']
    readable_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    if ":" in note_data:
        parts = note_data.split(":")
        clean_note = parts[0]
        beat = parts[1]
    else:
        clean_note = note_data
        beat = "1"
    
    octave_marker = ""
    if clean_note.endswith("+"):
        clean_note = clean_note[:-1]
        octave_marker = "'" 
    elif clean_note.endswith("-"):
        clean_note = clean_note[:-1]
        octave_marker = "," 
    else:
        clean_note = clean_note

    current_index = find_note_index(clean_note)
    if current_index == -1: return None, None, None

    remaining = target_value - source_value
    new_index = (current_index + remaining) % 12

    abc_code = abc_notes_map[new_index] + octave_marker
    readable_text = readable_notes[new_index]
    if octave_marker == "'": readable_text += "(+)"
    if octave_marker == ",": readable_text += "(-)"
    
    readable_notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    readable_text = readable_notes[new_index]
    
    return abc_code, readable_text, beat

# --- INTERFACE ---
st.title("🎷 Visual Note Converter")
st.write("Enter the notes; you can either see it translated or displayed on the sheet music.")
st.write("""
**Guide:**
* **Normal:** `A:1`
* **Fine:** `A+:1` (1 Octave Up)
* **Thick:** `A-:1` (1 Octace Down)
""")

# Sidebar
st.sidebar.header("Instruments Settings")
source_name = st.sidebar.selectbox("Source", list(INSTRUMENTS.keys()))
target_name = st.sidebar.selectbox("Target", list(INSTRUMENTS.keys()), index=1)

source_val = INSTRUMENTS[source_name]
target_val = INSTRUMENTS[target_name]

# Input
input_text = st.text_area("Enter notes (eg: C:2 D:2 E:4 F#:1)", value="C:2 D:2 E:4", height=80)

if st.button("Transpose and Create 🎼"):
    if input_text:
        raw_input = input_text.split()
        abc_output = []      
        text_display = []    
        
        for item in raw_input:
            abc_code, read_text, beat = transposer(item, source_val, target_val)
            if abc_code:
                if beat == "0.5":
                    formatted_beat = "/2"
                elif beat == "0.25":
                    formatted_beat = "/4"
                else:
                    formatted_beat = beat 
                abc_output.append(f"{abc_code}{beat}")
                text_display.append(f"{read_text}:{beat}")
        
        st.success("Transpose Success!")
        st.code(" ".join(text_display), language="text")
        
        abc_string = " ".join(abc_output)
        
        st.write("### 🎹 Sheet")
        
        html_code = f"""
        <script src="https://cdnjs.cloudflare.com/ajax/libs/abcjs/6.2.2/abcjs-basic-min.js"></script>
        <div id="paper"></div>
        <style>
            #paper {{
                background-color: white;
                padding: 10px;
                border-radius: 5px;
                border: 1px solid #ddd;
                text-align: center;
                min-height: 150px;
            }}
            svg {{ width: 100% !important; }}
        </style>
        <script type="text/javascript">
            var abc = "X:1\\nM:4/4\\nL:1/4\\nK:C\\n{abc_string}";
            ABCJS.renderAbc("paper", abc, {{ 
                responsive: "resize",
                add_classes: true
            }});
        </script>
        """
        components.html(html_code, height=300)
        
    else:
        st.warning("Please enter note.")