import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from google import genai

# --- 1. PAGE SETTINGS ---
st.set_page_config(page_title="🎷 Note Transposer AI", page_icon="🎵", layout="centered")

# --- 2. SESSION STATE (MEMORY) SETTINGS ---
# To retain the notes in memory even if the page is refreshed.
if 'input_text' not in st.session_state:
    st.session_state.input_text = "C:1 D:1 E:1"

# --- 3. API CONNECTION ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"API Connection Error: {e}")

# --- 4. CONSTANTS AND FUNCTIONS ---
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

def analyze_notes_with_ai(image_file):
    model_id = "gemini-flash-latest" 
    
    prompt = """
    Bu bir nota kağıdı görselidir. Lütfen sadece içindeki notaları ve vuruşlarını şu formatta yaz:
    Nota:Vuruş (Örn: C:1 D:0.5 E:2)
    Notalar arasında sadece bir boşluk bırak. Başka hiçbir açıklama yapma.
    Diyezleri #, bemolleri b olarak kullanabilirsin.
    """
    
    img = Image.open(image_file)
    try:
        response = client.models.generate_content(
            model=model_id,
            contents=[prompt, img]
        )
        return response.text
    except Exception as e:
        st.error(f"AI Error: {e}")
        return None

def transposer(note_data, source_value, target_value):
    # ABCJS and Readable Sheet Lists
    abc_notes_map = ['C', '^C', 'D', '_E', 'E', 'F', '^F', 'G', '_A', 'A', '_B', 'B']
    readable_notes = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
    
    # Break down input data (notes and beats).
    if ":" in note_data:
        parts = note_data.split(":")
        clean_note = parts[0]
        beat = parts[1]
    else:
        clean_note = note_data
        beat = "1"
    
    # Capture Octave Signals (+ or -)
    octave_marker = ""
    clean_note_only = clean_note 
    
    if clean_note.endswith("+"):
        clean_note_only = clean_note[:-1]
        octave_marker = "'" 
    elif clean_note.endswith("-"):
        clean_note_only = clean_note[:-1]
        octave_marker = "," 
    
    # Index and Transpose
    current_index = find_note_index(clean_note_only)
    if current_index == -1: return None, None, None

    remaining = target_value - source_value
    new_index = (current_index + remaining) % 12

    # Create Outputs
    abc_code = abc_notes_map[new_index] + octave_marker
    
    # Text Visible to the User
    readable_text = readable_notes[new_index]
    if octave_marker == "'": readable_text += "(+)"
    if octave_marker == ",": readable_text += "(-)"
    
    return abc_code, readable_text, beat

# --- 5.INTERFACE ---
st.title("🎷 AI Note Transposer")
st.markdown("Enter the sheet music, upload a photo, and convert it to your desired instrument..")

# -- Sidebar Settings --
st.sidebar.header("Instrument Settings")
source_name = st.sidebar.selectbox("Source Instrument", list(INSTRUMENTS.keys()), index=0)
target_name = st.sidebar.selectbox("Target Instrument", list(INSTRUMENTS.keys()), index=2)

source_val = INSTRUMENTS[source_name]
target_val = INSTRUMENTS[target_name]

st.sidebar.markdown("---")
st.sidebar.info("**Guide:**\n* Normal: `A:1`\n* Thin: `A+:1`\n* Bold: `A-:1")

# -- AI Part --
st.subheader("📸 Read Sheet from an Image")
uploaded_file = st.file_uploader("Upload a photo of the sheet music.", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    st.image(uploaded_file, caption='Uploaded Sheet', width=300)
    
    if st.button("Analyze with AI ✨"):
        with st.spinner("Artificial intelligence reads musical notes...."):
            detected_notes = analyze_notes_with_ai(uploaded_file)
            if detected_notes:
                # Refresh the memory and refresh the page
                st.session_state.input_text = detected_notes
                st.success("Notes readed!")
                st.rerun()

st.divider()

# -- Input Box (Reads from memory) --
# Memory is updated when the user modifies this box.
input_text = st.text_area(
    "Edit Sheet Music (Format: C:1 D:2)", 
    value=st.session_state.input_text, 
    height=100
)

# -- Transpose --
if st.button("Transpose 🎼"):
    st.session_state.input_text = input_text
    
    if input_text:
        raw_input = input_text.split()
        abc_output = []      
        text_display = []    
        
        for item in raw_input:
            abc_code, read_text, beat = transposer(item, source_val, target_val)
            if abc_code:
                abc_output.append(f"{abc_code}{beat}")
                text_display.append(f"{read_text}:{beat}")
        
        # Results
        st.success("Translation Successful!")
        st.code(" ".join(text_display), language="text")
        
        # ABCJS 
        abc_string = " ".join(abc_output)
        
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
                overflow-x: auto;
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
        components.html(html_code, height=350)
        
    else:
        st.warning("Please enter notes.")