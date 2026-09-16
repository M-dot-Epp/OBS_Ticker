# ====================================================
#  Stream Ticker
# ==============================================

# ==============================================
# This plugin is designed to add a "Sportscenter" style
# ticker side panel to show previous, current and upcoming topics
# The list of topics can be supplied through a text file that have
# the topics separated either by line or by commas
# ==================================================

import obspython as obs
import os

# ===============================================
# GLOBAL VARIABLES
# ===============================================

# Path where the script will render HTML output for the Browser Source in OBS
RUNDOWN_FILE_PATH = os.path.abspath(r"C:\Users\malik\Documents\OBS_Stream_Tickerobs_rundown.html")

# Global variables to store Hotkey IDs so OBS can track keybidings
HOTKEY_NEXT_ID = obs.OBS_INVALID_HOTKEY_ID
HOTKEY_PREV_ID = obs.OBS_INVALID_HOTKEY_ID

# ================================================
# STATE MANAGMENT VARIABLES
#=================================================

# Runtime state variables
topics_list = [] # Create list that will be populated by the topics from the txt file.
# list will be a 2D list as it will hold a value for the topic, and whether that topic is ACTIVE, UPCOMING, or COMPLETE
current_index = 0 # Track which topic is set to ACTIVE state. Initialized to first item
topics_file_path = "" # Will hold path to text file. Location will be specified in script properties

# ===============================================
# FILE PARSER & DATA PROCESSING
# ===============================================

# checks for duplicate topics in list and removes them from the list
def remove_duplicates(in_list):
    seen = set()
    seen_add = seen.add
    # return the list removing all duplicate topics case-insensitive
    return [x for x in in_list if x.lower() not in seen and not seen_add(x.lower())]

  


# Read text file and parses topics line by line or comma-separated.
# Adds to global 'topics_list' and sets first topic ("Intro") as 'ACTIVE'.

def load_topics_from_file(file_path):
    global topics_list, current_index

    # Check if provided path is valid and points to an existing file.
    if not file_path or not os.path.exists(file_path):
        print(f"[Rundown Script] File not found or path empty: {file_path}")
        return

# Create empty list for topics read from file
    raw_topics = []

    try:
        # Open file using 'with block (will auto-close file upon completion)
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip() # remove whitespace and new lines
                if not line_str:
                    continue #skip empty lines

                # Check line for comma-separated values
                if "," in line_str:
                    # split at the comma and remove whitespace of each split string.

                    split_items = [item.strip() for item in line_str.split(",") if item.strip()]
                    raw_topics.extend(split_items) # Add each item to raw list
                else:
                    # no comma separated value, only single topic
                    raw_topics.append(line_str)

    # Exception to catch errors while reading file
    except Exception as e:
        print(f"[Rundown Script] Error reading file: {e}")
        return

    # If valid topics were parsed, add to global topic list
    if raw_topics:
        # check for and remove duplicates
        clean_topics = remove_duplicates(raw_topics)
        topics_list = []
        # always initialize with "Intro" as first topic
        topics_list.append({
                "title": "Intro",
                "status": "UPCOMING"
            })
        # Add topics from file into data structure
        for title in clean_topics:
            topics_list.append({
                "title": title,
                "status": "UPCOMING"
            })

        # Set the first topic to ACTIVE by default
        current_index = 0
        topics_list[0]["status"] = "ACTIVE"

        # Render HTML file to reflect changes
        generate_html()
        print(f"[Rundown Script] successfully loaded {len(topics_list)} topics from file topics_file_path")

# =====================================================================================
# HTML RENDERING
# =====================================================================================

# Generates HTML/CSS file utilized by OBS Browser Source.
# Runs everytime the topics advance, regress, or reload
def generate_html():
    if not topics_list:
        #generate clean placeholder
        html_content = "<div class='header'>No Topics Loaded</div>"
    else:
        html_content = "<div class='header'>Rundown</div>"

        # Loop through each topic in list to build each HTML element dynamically
        for index, item in enumerate(topics_list): # enumerate() has a counter built in through the loop so you do not have to create and manually update a counter variable
            status = item["status"] # get status value of current list item
            title = item["title"] # get the title of the current list item

        # Style the elements depending on status ('ACTIVE', 'COMPLETE', 'UPCOMING')
            if status == "ACTIVE":
                badge = '<span class="badge active-badge">NOW</span>'
                item_class = "item active-item"
            elif status == "COMPLETE":
                    badge = '<span class="badge done-badge">✓</span>'
                    item_class = "item done-item"
            else:
                    badge = f'<span class="badge upcoming-badge">{index + 1}</span>'
                    item_class = "item upcoming-item"

            html_content += f"""
            <div class="{item_class}">
                {badge}
                <span class="title">{title}</span>
            </div>
            """

        # Full HTML Document Template
        # When writing HTML code in Python script, use double curly brackts ({}) as Python will interpret it as python code instead 
        # of plain text
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                * {{ box-sizing: border-box; margin: 0; padding: 0; }}
                body {{
                    font-family: 'Impact', 'Arial Black', sans-serif;
                    background: transparent;
                    color: #ffffff;
                    padding: 10px;
                    width: 320px;
                }}
                .rundown-container {{
                    background: linear-gradient(180deg, #111 0%, #222 100%);
                    border-left: 6px solid #e10600;
                    box-shadow: 0 10px 20px rgba(0,0,0,0.6);
                    border-radius: 4px;
                    overflow: hidden;
                }}
                .header {{
                    background: #e10600;
                    color: #fff;
                    padding: 8px 12px;
                    font-size: 16px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                .item {{
                    display: flex;
                    align-items: center;
                    padding: 10px 12px;
                    border-bottom: 1px solid #333;
                    font-size: 15px;
                    text-transform: uppercase;
                    transition: all 0.3s ease;
                }}
                .active-item {{
                    background: #ffffff;
                    color: #000000;
                    font-size: 17px;
                    font-weight: bold;
                    border-left: 4px solid #ffcc00;
                }}
                .done-item {{
                    color: #666666;
                    text-decoration: line-through;
                    background: #181818;
                }}
                .upcoming-item {{
                    color: #cccccc;
                }}
                .badge {{
                    display: inline-block;
                    padding: 2px 6px;
                    font-size: 11px;
                    border-radius: 2px;
                    margin-right: 10px;
                    min-width: 24px;
                    text-align: center;
                }}
                .active-badge {{ background: #e10600; color: #fff; }}
                .done-badge {{ background: #333; color: #888; }}
                .upcoming-badge {{ background: #444; color: #fff; }}
            </style>
        </head>
        <body>
            <div class="rundown-container">
                {html_content}
            </div>
            <!-- AUTO REFRESH SCRIPT -->
            <script>
                // Automatically updates the rundown container every second without reloading the page
                setInterval(function () {{
                    fetch('obs_rundown.html?t=' + Date.now())
                        .then(response => response.text())
                        .then(html => {{
                            var parser = new DOMParser();
                            var doc = parser.parseFromString(html, 'text/html');
                            var newContainer = doc.querySelector('.rundown-container');
                            if (newContainer) {{
                                document.querySelector('.rundown-container').innerHTML = newContainer.innerHTML;
                            }}
                        }})
                        .catch(err => console.log('Update check failed', err));
                    }}, 1000);
            </script>

        </body>
        </html>
        """

        # Overwrite the target HTML file on disk
        with open(RUNDOWN_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(full_html)


# ==============================================================================
# STATE NAVIGATION LOGIC
# ==============================================================================

def trigger_next():
    """Marks current topic as COMPLETE and sets the next topic as ACTIVE."""
    # Check if trigger_next is being applied
    print(f"Transition to Next Topic")
    global current_index
    if topics_list and current_index < len(topics_list) - 1:
        topics_list[current_index]["status"] = "COMPLETE"
        current_index += 1
        topics_list[current_index]["status"] = "ACTIVE"
        #print(f"Current topic is "topics_list[current_index]['title'])
        generate_html()

def trigger_prev():
    """Reverts active topic to UPCOMING and sets previous topic as ACTIVE."""
    # Check if trigger_prev is being applied
    print(f"Transition to previous Topic")
    global current_index
    if topics_list and current_index > 0:
        topics_list[current_index]["status"] = "UPCOMING"
        current_index -= 1
        topics_list[current_index]["status"] = "ACTIVE"
        generate_html()


# ==============================================================================
# CALLBACK FUNCTIONS FOR OBS UI AND HOTKEYS
# ==============================================================================

def cb_next_hotkey(pressed):
    """Callback executed when OBS detects the 'Next Topic' hotkey pressed."""
    if pressed:
        trigger_next()

def cb_prev_hotkey(pressed):
    """Callback executed when OBS detects the 'Prev Topic' hotkey pressed."""
    if pressed:
        trigger_prev()

def btn_reload_click(props, prop):
    """Callback executed when user clicks 'Reload Topics File' button in OBS UI."""
    global topics_file_path
    load_topics_from_file(topics_file_path)
    return True

def btn_next_click(props, prop):
    """Callback executed when user clicks 'Next Topic' button in OBS UI."""
    trigger_next()
    return True

def btn_prev_click(props, prop):
    """Callback executed when user clicks 'Previous Topic' button in OBS UI."""
    trigger_prev()
    return True


# ==============================================================================
# OBS PYTHON INTEGRATION HOOKS
# ==============================================================================

def script_description():
    """Returns description text displayed inside OBS Tools -> Scripts window."""
    return (
        "<b>Podcast Rundown Panel with File Loader</b><br>"
        "Loads topics from a .txt file (line-by-line or comma-separated).<br>"
        "Assign hotkeys in <i>Settings -> Hotkeys</i> to cycle topics live."
    )

def script_properties():
    """
    Constructs the GUI controls shown in OBS when clicking the script name.
    Creates a file picker path control and trigger buttons.
    """
    props = obs.obs_properties_create()

    # File Path Picker widget (filters specifically for .txt files)
    obs.obs_properties_add_path(
        props,
        "topics_file",
        "Select Topics File (.txt):",
        obs.OBS_PATH_FILE,
        "Text Files (*.txt);;All Files (*.*)",
        None
    )

    # Action Buttons
    obs.obs_properties_add_button(props, "btn_reload", "🔄 Reload Topics File", btn_reload_click)
    obs.obs_properties_add_button(props, "btn_prev", "◄ Previous Topic", btn_prev_click)
    obs.obs_properties_add_button(props, "btn_next", "Next Topic ►", btn_next_click)

    return props

def script_update(settings):
    """
    Called whenever user changes a setting in script properties window
    (such as picking a new text file).
    """
    global topics_file_path
    new_path = obs.obs_data_get_string(settings, "topics_file")

    # If user changed file path, update path and load topics automatically
    if new_path != topics_file_path:
        topics_file_path = new_path
        load_topics_from_file(topics_file_path)

def script_load(settings):
    """
    Called when OBS loads the script on boot or script refresh.
    Registers hotkeys and restores saved hotkey bindings.
    """
    global HOTKEY_NEXT_ID, HOTKEY_PREV_ID, topics_file_path

    # Initial HTML Render
    generate_html()

    # 1. Register Hotkeys with OBS Core
    HOTKEY_NEXT_ID = obs.obs_hotkey_register_frontend(
        "rundown_next_topic",
        "Rundown: Next Topic",
        cb_next_hotkey
    )
    HOTKEY_PREV_ID = obs.obs_hotkey_register_frontend(
        "rundown_prev_topic",
        "Rundown: Previous Topic",
        cb_prev_hotkey
    )

    # 2. Restore saved user hotkey combinations from OBS configuration data
    next_array = obs.obs_data_get_array(settings, "rundown_next_topic")
    obs.obs_hotkey_load(HOTKEY_NEXT_ID, next_array)
    obs.obs_data_array_release(next_array)

    prev_array = obs.obs_data_get_array(settings, "rundown_prev_topic")
    obs.obs_hotkey_load(HOTKEY_PREV_ID, prev_array)
    obs.obs_data_array_release(prev_array)

    # 3. Restore saved text file path and load file contents
    topics_file_path = obs.obs_data_get_string(settings, "topics_file")
    if topics_file_path:
        load_topics_from_file(topics_file_path)

def script_save(settings):
    """Called when OBS shuts down or saves settings; preserves hotkey bindings."""
    next_array = obs.obs_hotkey_save(HOTKEY_NEXT_ID)
    obs.obs_data_set_array(settings, "rundown_next_topic", next_array)
    obs.obs_data_array_release(next_array)

    prev_array = obs.obs_hotkey_save(HOTKEY_PREV_ID)
    obs.obs_data_set_array(settings, "rundown_prev_topic", prev_array)
    obs.obs_data_array_release(prev_array)